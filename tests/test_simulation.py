import pytest

from agents import ColorClaimCommunication, ScriptedCommunication, ScriptedDecision, SilentCommunication
from engine.transitions import GameEngine
from rules import Card, Condition, ConditionKind, GameConfig, GameMode, Succession
from simulation import AgentPolicy, SimulationError, SimulationLimitError, run_campaign, run_game, summarize


def quick_config(*, succession=Succession.REPLAY_RESPONSIBLE, donor_check=False,
                 refusal_visible=False, replay_visible=False, threshold=2, exact=False):
    defeat = Condition(ConditionKind.TOTAL_COUNT, threshold=threshold, exact=exact)
    return GameConfig({"rouge": 4, "bleu": 4}, GameMode.LAST_SURVIVOR,
                      (Card("a", defeat), Card("b", defeat)), succession=succession,
                      donor_defeat_after_removal=donor_check,
                      reveal_refusal_draw=refusal_visible, reveal_replay_draw=replay_visible,
                      initial_hand_size=1)


def talkative_policies():
    return {
        "a": AgentPolicy(ScriptedDecision(), ColorClaimCommunication(
            ("rouge", "bleu"), truthful=False, name="bluffing_donor")),
        "b": AgentPolicy(ScriptedDecision(), ScriptedCommunication(
            question_text="Quelle couleur ?", name="questioning_recipient")),
    }


def test_t63_complete_game_uses_controller_api_and_reproduces_with_same_seed():
    first = run_game(quick_config(), ["a", "b"], seed=765, first_player_id="a")
    second = run_game(quick_config(), ["a", "b"], seed=765, first_player_id="a")
    assert first == second
    assert first.outcome == "last_survivor" and first.winners == ("a",)
    assert first.actions == 3
    assert first.configuration["first_player_id"] == "a"
    assert first.configuration["round_starter_policy"] == "rotate_by_round_number"


def test_t10_t63_agents_execute_spontaneous_question_lie_response_and_silence_strategies():
    chatty = run_game(quick_config(), ["a", "b"], seed=52, first_player_id="a",
                      policies=talkative_policies())
    quiet = run_game(quick_config(), ["a", "b"], seed=52, first_player_id="a",
                     policies={"a": AgentPolicy(ScriptedDecision(), SilentCommunication()),
                               "b": AgentPolicy(ScriptedDecision(), SilentCommunication())})
    assert [message.kind.value for message in chatty.messages] == ["spontaneous", "question", "response"]
    assert [message.author_id for message in chatty.messages] == ["a", "b", "a"]
    assert len({message.proposal_id for message in chatty.messages}) == 1
    assert quiet.messages == ()
    assert (chatty.outcome, chatty.winners, chatty.actions) == (quiet.outcome, quiet.winners, quiet.actions)
    assert chatty.strategy_names["a"] == ("scripted", "bluffing_donor")
    assert chatty.strategy_names["b"] == ("scripted", "questioning_recipient")
    assert chatty.communication_modes["a"] == "deceptive"


def test_t10_agent_can_ask_a_question_and_choose_not_to_answer():
    run = run_game(quick_config(), ["a", "b"], seed=53, first_player_id="a",
                   policies={"a": AgentPolicy(ScriptedDecision(), SilentCommunication()),
                             "b": AgentPolicy(ScriptedDecision(), ScriptedCommunication(
                                 question_text="Quelle couleur ?"))})
    assert [message.kind.value for message in run.messages] == ["question"]


def test_t63_campaign_records_configuration_seed_strategies_and_descriptive_statistics():
    configs = {
        "A": quick_config(),
        "B": quick_config(succession=Succession.CLOCKWISE),
        "donor_check": quick_config(donor_check=True),
        "refusal_visible": quick_config(refusal_visible=True),
        "replay_visible": quick_config(replay_visible=True),
        "different_defeat": quick_config(exact=True),
    }
    profiles = {
        "silent": {"a": AgentPolicy(ScriptedDecision(), SilentCommunication()),
                   "b": AgentPolicy(ScriptedDecision(), SilentCommunication())},
        "chatty": talkative_policies(),
    }
    campaign = run_campaign(configs, ["a", "b"], seeds=[41, 42], first_player_id="a",
                            policy_profiles=profiles)
    assert len(campaign.runs) == 24
    assert len({run.configuration_name for run in campaign.runs}) == 12
    assert all(run.seed in (41, 42) and set(run.strategy_names) == {"a", "b"} for run in campaign.runs)
    a = next(run for run in campaign.runs if run.configuration_name == "A::silent" and run.seed == 41)
    b = next(run for run in campaign.runs if run.configuration_name == "B::silent" and run.seed == 41)
    assert a.configuration["succession"] == "A" and b.configuration["succession"] == "B"
    assert next(run for run in campaign.runs if run.configuration_name == "donor_check::silent").configuration["donor_defeat_after_removal"]
    assert next(run for run in campaign.runs if run.configuration_name == "refusal_visible::silent").configuration["reveal_refusal_draw"]
    assert next(run for run in campaign.runs if run.configuration_name == "replay_visible::silent").configuration["reveal_replay_draw"]
    assert "exact=True" in repr(next(run for run in campaign.runs if run.configuration_name == "different_defeat::silent").configuration["cards"])
    stats = summarize(campaign)
    assert stats.by_configuration["A::silent"]["games_completed"] == 2
    assert stats.by_configuration["A::silent"]["seeds"] == (41, 42)
    assert stats.by_configuration["A::silent"]["average_turns"] == 1
    assert stats.by_configuration["A::chatty"]["message_counts"] == {"spontaneous": 2, "question": 2, "response": 2}
    assert stats.by_configuration["A::chatty"]["messages_by_truthfulness_mode"]["deceptive"] == {
        "spontaneous": 2, "response": 2}
    assert not stats.errors


def test_t63_agents_receive_filtered_views_and_only_their_messages():
    class Spy:
        name = "spy"
        def __init__(self): self.observed = []
        def choose_action(self, view, legal_actions, messages):
            self.observed.append((view, messages))
            return ScriptedDecision().choose_action(view, legal_actions, messages)

    spy = Spy()
    policies = {"a": AgentPolicy(ScriptedDecision(), ScriptedCommunication(spontaneous_text="claim")),
                "b": AgentPolicy(spy, ScriptedCommunication(question_text="question"))}
    run_game(quick_config(), ["a", "b"], seed=5, first_player_id="a", policies=policies)
    recipient_decision = next((view, messages) for view, messages in spy.observed
                              if view.player_id == "b" and view.public.proposal is not None)
    assert recipient_decision[0].offered_token is None
    assert [message.kind.value for message in recipient_decision[1]] == ["spontaneous", "question"]
    assert all(message.author_id in {"a", "b"} for message in recipient_decision[1])


def test_t63_invariant_failures_and_action_limits_are_reported_explicitly(monkeypatch):
    def broken_check(self):
        raise AssertionError("token inventory mismatch")
    monkeypatch.setattr(GameEngine, "assert_invariants", broken_check)
    with pytest.raises(SimulationError, match="Échec de simulation") as error:
        run_game(quick_config(), ["a", "b"], seed=8, first_player_id="a")
    assert isinstance(error.value.__cause__, AssertionError)
    monkeypatch.undo()
    with pytest.raises(SimulationLimitError, match="Limite de 1 actions"):
        run_game(quick_config(threshold=99), ["a", "b"], seed=8,
                 first_player_id="a", max_actions=1)


def test_t63_campaign_can_record_failures_without_mixing_them_into_completed_statistics():
    campaign = run_campaign({"finite": quick_config()}, ["a", "b"], seeds=[1],
                            first_player_id="a", max_actions=1, continue_on_error=True)
    assert not campaign.runs and len(campaign.errors) == 1
    assert summarize(campaign).by_configuration["finite::default"]["errors"] == 1

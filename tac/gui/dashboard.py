# -*- coding: utf-8 -*-
import argparse
import inspect
import json
import os
import subprocess
import time
from typing import Optional

import numpy as np
from visdom import Visdom

from tac.game import Game
from tac.stats import GameStats

CUR_PATH = inspect.getfile(inspect.currentframe())
CUR_DIR = os.path.dirname(CUR_PATH)
ROOT_PATH = os.path.join(CUR_DIR, "..", "..")

viz = None  # type: Optional[Visdom]
env_main_name = "sim_main"
env_txs_name = "sim_txs"


def _start_visdom_server() -> subprocess.Popen:
    visdom_server_args = ["python", "-m", "visdom.server", "-env_path", os.path.join(CUR_DIR, ".visdom_env")]
    print(" ".join(visdom_server_args))
    prog = subprocess.Popen(visdom_server_args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    print("Visdom server running at http://localhost:8097")
    return prog


class Dashboard(object):
    """Class to manage Visdom dashboard."""

    def __init__(self, game_stats: GameStats):
        self._proc = None  # type: Optional[subprocess.Popen]
        self.viz = None  # type: Optional[Visdom]
        self.game_stats = game_stats

    def _is_running(self):
        return self._proc is not None and self.viz is not None

    def start(self):
        self._proc = _start_visdom_server()
        self.viz = Visdom()

    def stop(self):
        if self._is_running():
            self._proc.terminate()
            self.viz.close()
        self._proc = None
        self.viz = None

    def update(self):
        self._update_info()
        self._update_utilities()
        self._update_current_holdings()
        self._update_initial_holdings()
        self._update_plot_scores()
        self._update_plot_balance_history()
        self._update_current_balances()

    @staticmethod
    def from_datadir(datadir: str):
        game_data_json_filepath = os.path.join(datadir, "game.json")
        print("Loading data from {}".format(game_data_json_filepath))
        game_data = json.load(open(game_data_json_filepath))
        game = Game.from_dict(game_data)
        game_stats = GameStats(game)
        return Dashboard(game_stats)

    def _update_info(self):
        window_name = "configuration_details"
        self.viz.properties([
            {'type': 'number', 'name': '# agents', 'value': self.game_stats.game.configuration.nb_agents},
            {'type': 'number', 'name': '# goods', 'value': self.game_stats.game.configuration.nb_goods},
            {'type': 'number', 'name': 'fee', 'value': self.game_stats.game.configuration.fee},
            {'type': 'number', 'name': 'initial balance',
             'value': self.game_stats.game.configuration.initial_money_amounts[0]},
            {'type': 'number', 'name': '# transactions', 'value': len(self.game_stats.game.transactions)},
        ], env=env_main_name, win=window_name, opts=dict(title="Configuration"))

    def _update_utilities(self):
        utilities = self.game_stats.game.configuration.utilities
        utilities = np.asarray(utilities)

        window_name = "utilities"
        self.viz.heatmap(utilities, env=env_main_name, win=window_name, opts=dict(
            title="Utilities",
            xlabel="Goods",
            ylabel="Agents"
        ))

    def _update_current_balances(self):
        balances = np.asarray([state.balance for state in self.game_stats.game.agent_states])
        self.viz.bar(X=balances, env=env_main_name, win="balances", opts=dict(title="Balances"))

    def _update_initial_holdings(self):
        initial_holdings = self.game_stats.holdings_history()[0]
        self.viz.heatmap(initial_holdings, env=env_main_name, win="initial_holdings", opts=dict(
            title="Initial Holdings",
            xlabel="Goods",
            ylabel="Agents",
            stacked=True,
        ))

    def _update_current_holdings(self):
        initial_holdings = self.game_stats.holdings_history()[-1]
        self.viz.heatmap(initial_holdings, env=env_main_name, win="final_holdings", opts=dict(
            title="Current Holdings",
            xlabel="Goods",
            ylabel="Agents",
            stacked=True,
        ))

    def _update_plot_scores(self):
        score_history = self.game_stats.score_history()

        window_name = "score_history"
        self.viz.line(X=np.arange(score_history.shape[0]), Y=score_history, env=env_main_name, win=window_name, opts=dict(
            legend=self.game_stats.game.configuration.agent_labels,
            title="Scores",
            xlabel="Transactions",
            ylabel="Score"
        ))

    def _update_plot_balance_history(self):
        balance_history = self.game_stats.balance_history()

        window_name = "Balances history"
        self.viz.line(X=np.arange(balance_history.shape[0]), Y=balance_history, env=env_main_name, win=window_name,
                 opts=dict(
                     legend=self.game_stats.game.configuration.agent_labels,
                     title="Balance history",
                     xlabel="Transactions",
                     ylabel="Money"
                 ))

    def __enter__(self):
        d.start()
        d.update()

    def __exit__(self, exc_type, exc_val, exc_tb):
        d.stop()


def parse_args():
    parser = argparse.ArgumentParser("dashboard", description="Data Visualization for the simulation outcome")
    parser.add_argument("--datadir", type=str, required=True, help="The path to the simulation data folder.")

    arguments = parser.parse_args()
    return arguments


if __name__ == '__main__':

    arguments = parse_args()

    datadir = arguments.datadir
    d = Dashboard.from_datadir(datadir)

    with d:
        while True:
            input()

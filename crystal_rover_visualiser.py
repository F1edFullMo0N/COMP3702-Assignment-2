"""Plot CrystalRover state values and policy for one crystal bitmask.

Place this beside solution.py, game_env.py and game_state.py, then run e.g.:
    python crystal_rover_visualiser.py testcases/L1.txt --method vi
    python crystal_rover_visualiser.py testcases/L1.txt --method vi --mask 111

AI assistance: OpenAI Codex (GPT-6), 24 Sep 2026. Generated in response to
the user's request for a Q2(c) policy-and-value visualiser, using the supplied
CrystalRover Solver and GameEnv interfaces. Verify output before submission.
"""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

from game_env import GameEnv
from solution import Solver


COLORS = {
    "R": "#525866",  # rock
    "L": "#db6d5b",  # lava
    "*": "#d9bc88",  # crater
    "C": "#f3dc82",  # crystal
    "E": "#84c7ad",  # launch site
    "P": "#86b5e3",  # initial rover position
    " ": "#f8f8f6",  # ground
}


def tile_symbol(env, row, col, status):
    pos = (row, col)
    if pos == (env.init_row, env.init_col):
        return "P"
    if pos in env.crystal_positions:
        i = env.crystal_positions.index(pos)
        if status[i] == 0:
            return "C"
    return env.grid_data[row][col]


def draw(env, solver, method, status, destination):
    if method == "vi":
        states = solver.vi_states
        values = solver.vi_values
        action_for = solver.vi_select_action
    else:
        states = solver.pi_states
        values = solver.pi_values
        action_for = solver.pi_select_action

    # A coordinate alone does not identify a state: crystal_status matters.
    visible_states = {
        (s.row, s.col): s for s in states if s.crystal_status == status
    }
    fig, ax = plt.subplots(
        figsize=(max(7.5, env.n_cols * 0.9), max(4.5, env.n_rows * 0.9))
    )

    for row in range(env.n_rows):
        for col in range(env.n_cols):
            tile = tile_symbol(env, row, col, status)
            ax.add_patch(
                Rectangle(
                    (col, row), 1, 1,
                    facecolor=COLORS.get(tile, COLORS[" "]),
                    edgecolor="#b8bec4", linewidth=0.9,
                )
            )
            if tile != " ":
                ax.text(
                    col + 0.09, row + 0.18, tile,
                    fontsize=9, fontweight="bold",
                    color="white" if tile in {"R", "L"} else "#263238",
                    va="center",
                )

            state = visible_states.get((row, col))
            if state is None:
                continue
            value = values.get(state)
            if value is None:
                continue
            if env.is_game_over(state) or env.is_solved(state):
                action = "terminal"
            else:
                action = action_for(state)
            ax.text(
                col + 0.5, row + 0.56,
                f"{value:.2f}\n{action}",
                ha="center", va="center", fontsize=8,
                color="white" if tile in {"R", "L"} else "#15232d",
                fontweight="normal",
            )

    ax.set_xlim(0, env.n_cols)
    ax.set_ylim(env.n_rows, 0)
    ax.set_aspect("equal")
    ax.set_xticks([i + 0.5 for i in range(env.n_cols)], range(env.n_cols))
    ax.set_yticks([i + 0.5 for i in range(env.n_rows)], range(env.n_rows))
    ax.tick_params(length=0, labelsize=8)
    for side in ax.spines.values():
        side.set_visible(False)

    ax.set_title(
        f"CrystalRover {method.upper()} values and policy  |  "
        f"crystals: {''.join(map(str, status))}\n"
        f"gamma={env.gamma:g}, epsilon={env.epsilon:g}",
        fontsize=10, pad=11,
    )
    ax.legend(
        handles=[Patch(facecolor=c, label=label) for label, c in [
            ("Rock", COLORS["R"]), ("Lava", COLORS["L"]),
            ("Crater", COLORS["*"]), ("Uncollected crystal", COLORS["C"]),
            ("Launch site", COLORS["E"]), ("Initial position", COLORS["P"]),
        ]],
        loc="upper center", bbox_to_anchor=(0.5, -0.02),
        ncol=3, frameon=False, fontsize=8,
    )
    fig.text(
        0.5, 0.025,
        "Each visited tile shows V(s) above its action for the selected crystal status.\n"
        "Empty tiles have no reachable state with this status.",
        ha="center", fontsize=8, color="#48515a",
    )
    fig.subplots_adjust(left=0.08, right=0.98, top=0.82, bottom=0.25)
    fig.savefig(destination, dpi=200, facecolor="white")
    plt.close(fig)
    return len(visible_states)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("testcase", help="Path such as testcases/L1.txt")
    parser.add_argument("--method", choices=("vi", "pi"), default="vi")
    parser.add_argument("--mask", help="Crystal collection bits, e.g. 001; default: all zero")
    parser.add_argument("--output", help="Output PNG filename")
    args = parser.parse_args()

    env = GameEnv(args.testcase)
    status = env.get_init_state().crystal_status
    if args.mask is not None:
        if len(args.mask) != len(status) or set(args.mask) - {"0", "1"}:
            parser.error(f"--mask must contain exactly {len(status)} binary digits")
        status = tuple(int(bit) for bit in args.mask)

    solver = Solver(env)
    if args.method == "vi":
        solver.vi_plan_offline()
    else:
        solver.pi_plan_offline()

    default_name = f"{Path(args.testcase).stem}_{args.method}_{''.join(map(str, status))}.png"
    destination = Path(args.output or default_name)
    count = draw(env, solver, args.method, status, destination)
    print(f"Saved {destination} ({count} reachable states in this bitmask view)")


if __name__ == "__main__":
    main()

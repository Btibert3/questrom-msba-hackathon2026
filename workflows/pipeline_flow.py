import os
import datetime
import statsapi
import duckdb
import pandas as pd
from dotenv import load_dotenv
from prefect import flow, task

load_dotenv()


@task
def get_game_ids(date: str) -> list[int]:
    games = statsapi.schedule(start_date=date, end_date=date)
    print(f"Found {len(games)} games on {date}")
    return [g["game_id"] for g in games]


@task
def fetch_pitches(game_ids: list[int], game_date: str) -> pd.DataFrame:
    rows = []
    for gid in game_ids:
        data = statsapi.get("game", {"gamePk": gid})
        game_data = data["gameData"]
        away_team = game_data["teams"]["away"]["name"]
        home_team = game_data["teams"]["home"]["name"]
        all_plays = data["liveData"]["plays"]["allPlays"]

        for play in all_plays:
            about = play.get("about", {})
            inning = about.get("inning")
            half_inning = about.get("halfInning")
            at_bat_result = play.get("result", {}).get("event")

            offense = play.get("matchup", {})
            pitcher_name = offense.get("pitcher", {}).get("fullName")
            batter_name = offense.get("batter", {}).get("fullName")

            runners = play.get("runners", [])
            on_1b = any(r.get("movement", {}).get("end") == "1B" or r.get("movement", {}).get("start") == "1B" for r in runners)
            on_2b = any(r.get("movement", {}).get("end") == "2B" or r.get("movement", {}).get("start") == "2B" for r in runners)
            on_3b = any(r.get("movement", {}).get("end") == "3B" or r.get("movement", {}).get("start") == "3B" for r in runners)

            play_events = play.get("playEvents", [])
            last_pitch_idx = max(
                (i for i, e in enumerate(play_events) if e.get("isPitch")),
                default=None,
            )

            for i, event in enumerate(play_events):
                if not event.get("isPitch"):
                    continue

                details = event.get("details", {})
                pitch_data = event.get("pitchData", {})
                count = event.get("count", {})

                rows.append({
                    "game_pk": gid,
                    "game_date": game_date,
                    "away_team": away_team,
                    "home_team": home_team,
                    "inning": inning,
                    "half_inning": half_inning,
                    "pitcher_name": pitcher_name,
                    "batter_name": batter_name,
                    "pitch_type": details.get("type", {}).get("code"),
                    "pitch_description": details.get("type", {}).get("description"),
                    "description": details.get("description"),
                    "start_speed": pitch_data.get("startSpeed"),
                    "end_speed": pitch_data.get("endSpeed"),
                    "zone": pitch_data.get("zone"),
                    "balls": count.get("balls"),
                    "strikes": count.get("strikes"),
                    "away_score": count.get("awayScore"),
                    "home_score": count.get("homeScore"),
                    "on_1b": on_1b,
                    "on_2b": on_2b,
                    "on_3b": on_3b,
                    "events": at_bat_result if i == last_pitch_idx else None,
                })

    df = pd.DataFrame(rows)
    print(f"Fetched {len(df)} pitches across {len(game_ids)} games")
    return df


@task
def load_to_motherduck(df: pd.DataFrame, table: str = "pitches") -> int:
    token = os.environ["MOTHERDUCK_TOKEN"]
    con = duckdb.connect(f"md:?motherduck_token={token}")
    con.execute("CREATE DATABASE IF NOT EXISTS hackathon")
    con.execute("USE hackathon")
    con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM df")
    count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    con.close()
    print(f"Loaded {count} rows into MotherDuck table '{table}'")
    return count


@flow(name="pipeline-flow")
def pipeline_flow():
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    game_ids = get_game_ids(yesterday)
    if not game_ids:
        print("No games yesterday — nothing to load.")
        return
    df = fetch_pitches(game_ids, yesterday)
    load_to_motherduck(df)


if __name__ == "__main__":
    pipeline_flow()

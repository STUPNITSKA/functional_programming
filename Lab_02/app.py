import argparse
import json
from pathlib import Path

from core import Record, Stats, build_pipeline, reduce_stats


def read_tracks(path: Path) -> list[Record]:
    data: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("expected a JSON list of tracks")
    tracks: list[Record] = []
    for item in data:
        if not isinstance(item, dict):
            raise ValueError("each track must be a JSON object")
        listens = item.get("listens")
        if not isinstance(listens, list) or not all(
            isinstance(x, int) for x in listens
        ):
            raise ValueError("listens must be a list of integers")
        tracks.append(
            {
                "id": int(item["id"]),
                "title": str(item["title"]),
                "genre": str(item["genre"]),
                "listens": listens,
            }
        )
    return tracks


def print_rating(rating: list[Record], stats: Stats) -> None:
    for place, track in enumerate(rating, start=1):
        print(
            f"{place}. {track['title']} ({track['genre']}, id {track['id']}): "
            f"{track.get('total', 0.0):g}"
        )
    print(
        f"count: {stats['count']}, listens_sum: {stats['listens_sum']:g}, "
        f"avg_listens: {stats['avg_listens']:g}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Музичний каталог")
    parser.add_argument(
        "--data", type=Path, default=Path(__file__).with_name("sample_data.json")
    )
    parser.add_argument("--top", type=int, default=3)
    parser.add_argument("--boost-genre", default="Рок")
    parser.add_argument("--factor", type=float, default=1.1)
    parser.add_argument("--min-listens", type=float, default=100)
    args = parser.parse_args(argv)

    try:
        tracks = read_tracks(args.data)
        pipeline = build_pipeline(
            top_n=args.top,
            genre=args.boost_genre,
            factor=args.factor,
            min_listens=args.min_listens,
        )
        rating = pipeline(tracks)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))

    print_rating(rating, reduce_stats(rating))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

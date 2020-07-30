import csv
from typing import Iterable, Callable, cast
from pydfs_lineup_optimizer.lineup import Lineup
from pydfs_lineup_optimizer.player import LineupPlayer


class LineupExporter:
    def __init__(self, lineups: Iterable[Lineup]):
        self.lineups = lineups

    @staticmethod
    def render_player(player: LineupPlayer) -> str:
        result = player.full_name  # type: str
        if player.id:
            result += '(%s)' % player.id
        return result

    def export(self, filename: str, render_func: Callable[[LineupPlayer], str] = None):
        raise NotImplementedError


class CSVLineupExporter(LineupExporter):
    def export(self, filename, render_func=None):
        with open(filename, 'w') as csvfile:
            lineup_writer = csv.writer(csvfile, delimiter=',')
            for index, lineup in enumerate(self.lineups):
                if index == 0:
                    header = [
                        player.lineup_position for player in lineup.lineup]
                    header.extend(('Budget', 'FPPG'))
                    lineup_writer.writerow(header)
                row = [(render_func or self.render_player)(player)
                       for player in lineup.lineup]
                row.append(str(lineup.salary_costs))
                row.append(str(lineup.fantasy_points_projection))
                lineup_writer.writerow(row)


class FantasyDraftCSVLineupExporter(LineupExporter):
    def export(self, filename, render_func=None):
        if not self.lineups:
            return
        total_players = 0
        with open(filename, 'r') as csvfile:
            lines = list(csv.reader(csvfile))
            for i, lineup in enumerate(self.lineups, start=1):
                if i >= len(lines):
                    lines.append([])
                players_list = [(render_func or self.render_player)(
                    player) for player in lineup.lineup]
                if not total_players:
                    total_players = len(players_list)
                lines[i] = players_list + lines[i][total_players:]
            for line_order in range(i, len(lines) - 1):
                lines[line_order] = [''] * total_players + \
                    lines[line_order][total_players:]
        with open(filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(lines)


class JSONLineupExporter(LineupExporter):
    def export(self, render_func=None):
        totalLineups = {
            "lineups": []
        }
        for index, lineup in enumerate(self.lineups):
            lineupList = []

            # Generate players id
            for player in lineup.lineup:
                lineupList.append(player.id)

            # Generate lineup JSON object
            lineupJSON = {
                "players": lineupList,
                "totalSalary": lineup.salary_costs,
                "totalFppg": lineup.fantasy_points_projection
            }
            totalLineups["lineups"].append(lineupJSON)
        return totalLineups

from bs4 import BeautifulSoup
import logging
import requests

logging.basicConfig(level=logging.INFO)


class RatCatcher:

    def __init__(self, player, interval=60, verbose=0):
        logging.info("Initializing...")
        self.player = player
        self.interval = interval
        self.verbose = verbose
        self.stack = []
        self.stats = {}
        self.get_ladder_status()

    def get_ladder_status(self):
        """Consume ladder request and get the output in HTML format."""
        url = "https://play.pokemonshowdown.com/ladder.php?format=gen9randombattle&server=showdown&output=html"
        response = requests.request("GET", url)
        parsed_ladder = self.parse_ladder(response.text)
        self.stack.append(parsed_ladder)
        logging.info("Ladder status updated.")

    @staticmethod
    def parse_ladder(html_code):
        """Parse the response of a get ladder request."""
        soup = BeautifulSoup(html_code, 'html.parser')
        table = soup.find('table')
        rows = table.find_all('tr')
        ladder = {}
        for row in rows[1:]:  # Skip the header row
            cells = row.find_all('td')
            name = cells[1].text
            elo = int(cells[2].strong.text)
            ladder[name] = elo
        return ladder

    def elo_changed(self, tol=-5):
        """Check if the ELO of the target player changed."""
        try:
            target_delta = self.new[self.player] - self.old[self.player]
            if target_delta > 0 or target_delta < tol:
                return target_delta
            else:
                return False
        except KeyError:
            logging.error("Not enough ladder snapshots. Fetch at least two ladder snapshots.")

    def get_opponent(self, target_delta):
        """Find opponent of target player comparing ELO changes in the ladder."""
        for other in self.new:
            other_delta = self.new[other] - self.old[other]
            if other_delta == -target_delta:
                result = 'loss' if target_delta < 0 else 'win'
                return other, result
        return

    def update_stats(self, opponent):
        """Update target player W/L statistics"""
        name, result = opponent
        if name not in self.stats:
            self.stats[name] = {}
        self.stats[name][result] += 1
        if self.verbose > 0:
            logging.info(self.stats)

    def start(self):
        """Run the rat recognition engine."""
        while True:
            time.sleep(self.interval)
            self.get_ladder_status()
            if target_delta := self.elo_changed():
                opponent = self.get_opponent(target_delta)
                if opponent:
                    self.update_stats(opponent)
                else:
                    logging.warning("No opponent found despite significant delta score")

    @property
    def new(self):
        return self.stack[-1]

    @property
    def old(self):
        return self.stack[-2]


if __name__ == '__main__':
    import time
    rt = RatCatcher('dualipa w dababy', verbose=1)
    rt.start()

import re
from .constants import (DAY,
                        NIGHT,
                        SCHEDULE_SCHEME,
                        SCHEDULE_URL)
from datetime import datetime
from pyquery import PyQuery as pq
from sportsreference import utils
from sportsreference.constants import (WIN,
                                       LOSS,
                                       HOME,
                                       AWAY,
                                       NEUTRAL,
                                       REGULAR_SEASON,
                                       CONFERENCE_TOURNAMENT)
from sportsreference.mlb.boxscore import Boxscore


class Game(object):
    """
    A representation of a matchup between two teams.

    Stores all relevant high-level match information for a game in a team's
    schedule including date, time, opponent, and result.
    """
    def __init__(self, game_data, year):
        """
        Parse all of the attributes located in the HTML data.

        Parameters
        ----------
        game_data : string
            The row containing the specified game information.
        year : string
            The year of the current season.
        """
        self._game = None
        self._date = None
        self._datetime = None
        self._boxscore = None
        self._location = None
        self._opponent_abbr = None
        self._result = None
        self._runs_scored = None
        self._runs_allowed = None
        self._innings = None
        self._record = None
        self._rank = None
        self._games_behind = None
        self._winner = None
        self._loser = None
        self._save = None
        self._game_duration = None
        self._day_or_night = None
        self._attendance = None
        self._streak = None
        self._year = year

        self._parse_game_data(game_data)

    def _parse_boxscore(self, game_data):
        """
        Parses the boxscore URI for the game.

        The boxscore is embedded within the HTML tag and needs a special
        parsing scheme in order to be extracted.
        """
        boxscore = game_data('td[data-stat="boxscore"]:first')
        boxscore = re.sub(r'.*/boxes/', '', str(boxscore))
        boxscore = re.sub(r'\.shtml.*', '', boxscore)
        setattr(self, '_boxscore', boxscore)

    def _parse_game_data(self, game_data):
        """
        Parses a value for every attribute.

        The function looks through every attribute with the exception of those
        listed below and retrieves the value according to the parsing scheme
        and index of the attribute from the passed HTML data. Once the value
        is retrieved, the attribute's value is updated with the returned
        result.

        Note that this method is called directory once Game is invoked and does
        not need to be called manually.

        Parameters
        ----------
        game_data : string
            A string containing all of the rows of stats for a given game.
        """
        for field in self.__dict__:
            # Remove the leading '_' from the name
            short_name = str(field)[1:]
            if short_name == 'datetime' or \
               short_name == 'year':
                continue
            elif short_name == 'boxscore':
                self._parse_boxscore(game_data)
                continue
            value = utils._parse_field(SCHEDULE_SCHEME, game_data, short_name)
            setattr(self, field, value)

    @property
    def game(self):
        """
        Returns an int of the game in the season, where 1 is the first game of
        the season.
        """
        return int(self._game)

    @property
    def date(self):
        """
        Returns a string of the date the game was played on.
        """
        return self._date

    @property
    def datetime(self):
        """
        Returns a datetime object of the month, day, year, and time the game
        was played.
        """
        date_string = '%s %s' % (self._date, self._year)
        return datetime.strptime(date_string, '%A, %b %d %Y')

    @property
    def boxscore(self):
        """
        Returns an instance of the Boxscore class containing more detailed
        stats on the game.
        """
        return Boxscore(self._boxscore)

    @property
    def location(self):
        """
        Returns a string constant to indicate whether the game was played at
        home or away.
        """
        if self._location == '@':
            return AWAY
        return HOME

    @property
    def opponent_abbr(self):
        """
        Returns a string of the opponent's 3-letter abbreviation, such as 'NYY'
        for the New York Yankees.
        """
        return self._opponent_abbr

    @property
    def result(self):
        """
        Returns a string constant to indicate whether the team won or lost.
        """
        if self._result.lower() == 'w':
            return WIN
        return LOSS

    @property
    def runs_scored(self):
        """
        Returns an int of the total number of runs that were scored by the
        team.
        """
        return int(self._runs_scored)

    @property
    def runs_allowed(self):
        """
        Returns an int of the total number of runs that the team allowed.
        """
        return int(self._runs_allowed)

    @property
    def innings(self):
        """
        Returns an int of the total number of innings that were played.
        """
        if not self._innings:
            return 9
        return int(self._innings)

    @property
    def record(self):
        """
        Returns a string of the team's record in the format 'W-L'.
        """
        return self._record

    @property
    def rank(self):
        """
        Returns an int of the team's rank in the league with 1 being the best
        team.
        """
        return int(self._rank)

    @property
    def games_behind(self):
        """
        Returns a float of the number of games behind the leader the team is.
        0.0 indicates the team is tied for first. Negative numbers indicate the
        number of games a team is ahead of the second place team.
        """
        if 'up' in self._games_behind.lower():
            games_behind = re.sub('up *', '', self._games_behind.lower())
            return float(games_behind) * -1.0
        if 'tied' in self._games_behind.lower():
            return 0.0
        return float(self._games_behind)

    @property
    def winner(self):
        """
        Returns a string of the name of the winning pitcher.
        """
        return self._winner

    @property
    def loser(self):
        """
        Returns a string of the name of the losing pitcher.
        """
        return self._loser

    @property
    def save(self):
        """
        Returns a string of the name of the pitcher credited with the save if
        applicable. If no saves, returns None.
        """
        if self._save == '':
            return None
        return self._save

    @property
    def game_duration(self):
        """
        Returns a string of the game's total duration in the format 'H:MM'.
        """
        return self._game_duration

    @property
    def day_or_night(self):
        """
        Returns a string constant to indicate whether the game was played
        during the day or night.
        """
        if self._day_or_night.lower() == 'n':
            return NIGHT
        return DAY

    @property
    def attendance(self):
        """
        Returns an int of the total listed attendance for the game.
        """
        return int(self._attendance.replace(',', ''))

    @property
    def streak(self):
        """
        Returns a string of the team's winning/losing streak at the conclusion
        of the requested game. A winning streak is denoted by a number of '+'
        signs for the number of consecutive wins and a losing streak is denoted
        by a '-' sign.
        """
        return self._streak


class Schedule:
    """
    An object of the given team's schedule.

    Generates a team's schedule for the season including wins, losses, and
    scores if applicable.
    """
    def __init__(self, abbreviation, year=None):
        """
        Parameters
        ----------
        abbreviation : string
            A team's short name, such as 'HOU' for the Houston Astros.
        year : string (optional)
            The requested year to pull stats from.
        """
        self._games = []
        self._pull_schedule(abbreviation, year)

    def __getitem__(self, index):
        """
        Return a specified game.

        Returns a specified game as requested by the index number in the array.
        The input index is 0-based and must be within the range of the schedule
        array.

        Parameters
        ----------
        index : int
            The 0-based index of the game to return.

        Returns
        -------
        Game instance
            If the requested game can be found, its Game instance is returned.
        """
        return self._games[index]

    def __call__(self, date):
        """
        Return a specified game.

        Returns a specific game as requested by the passed datetime. The input
        datetime must have the same year, month, and day, but can have any time
        be used to match the game.

        Parameters
        ----------
        date : datetime
            A datetime object of the month, day, and year to identify a
            particular game that was played.

        Returns
        -------
        Game instance
            If the requested game can be found, its Game instance is returned.

        Raises
        ------
        ValueError
            If the requested date cannot be matched with a game in the
            schedule.
        """
        for game in self._games:
            if game.datetime.year == date.year and \
               game.datetime.month == date.month and \
               game.datetime.day == date.day:
                return game
        raise ValueError('No games found for requested date')

    def __repr__(self):
        """Returns a list of all games scheduled for the given team."""
        return self._games

    def __iter__(self):
        """
        Returns an iterator of all of the games scheduled for the given team.
        """
        return iter(self.__repr__())

    def __len__(self):
        """Returns the number of scheduled games for the given team."""
        return len(self.__repr__())

    def _pull_schedule(self, abbreviation, year):
        """
        Parameters
        ----------
        abbreviation : string
            A team's short name, such as 'HOU' for the Houston Astros.
        year : string
            The requested year to pull stats from.
        """
        if not year:
            year = utils._find_year_for_season('mlb')
        doc = pq(SCHEDULE_URL % (abbreviation, year))
        schedule = utils._get_stats_table(doc, 'table#team_schedule')

        for item in schedule:
            if 'class="thead"' in str(item):
                continue
            game = Game(item, year)
            self._games.append(game)
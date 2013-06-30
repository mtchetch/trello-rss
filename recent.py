"""
recent.py - Used for trello-rss to grab recent Trello updates on your account
Written by Nate Collings
Last Update: June 30, 2013

Required:

sarumont's py-trello Trello API Wrapper:
https://github.com/sarumont/py-trello

TODO:
- Currently only supports newly created cards, boards, lists, and comments. Add support for more
- Currently just retrieves ALL it can given a specific token. Add support for just getting
  updates for certain boards, public or otherwise.

"""

from trello import TrelloClient
from datetime import datetime
import json


class InvalidItem(Exception):
    """Raised when a user calls for an item that is not supported"""
    pass


class Recent:
    """
    Class used to retrieve recent Trello updates. Uses sarumont's py-trello API wrapper lightly.
    Currently I just grab the full lump of data from the board API call. 
    
    For my use of Trello this works just fine, but if you're using it really 
    heavily I could see this using up too much memory, or the resultant xml being too big or something.
    Could improve that by specifying exactly what we want with the ?filter param, or digging into using
    the lists/cards apis more directly. I'm not going to worry about that too much right now,
    unless anybody has issues with it.

    Really needs support for the other actions.

    """

    def __init__(self, api_key, token):
        self.api_key = api_key
        self.token = token
        self.trell = TrelloClient(self.api_key, self.token)
        self.boards = None # Lazy, so doesn't fetch until we ask for them

        # A list of items currently supported. The user should pass in one of the keys below,
        # and we use the values when passing it to the Trello API.
        self.items = {'cards': 'createCard', 'boards': 'createBoard', 'lists': 'createList', 'comments': 'commentCard'}


    def create_date(self, date):
        return datetime.strptime(date[:-5], '%Y-%m-%dT%H:%M:%S')

    def get_activity(self, filter, boards):
        """Given a filter, returns those actions for boards from the Trello API"""
        actions = []
        for board in boards:
            # TODO: Let the user specify if they want closed boards too
            if board.closed is False:
                board.fetch_actions(filter)
                if len(board.actions) > 0:
                    actions.append(board.actions)
        return actions

    def get_boards(self):
        """
        Calls the list_boards() function if we haven't alreadyi
        
        TODO: Gets all a user's boards currently. Let the user specify
        which board they want (by title or ID?), or public boards (don't need
        a token).

        """

        if self.boards is None:
            self.boards = self.trell.list_boards()
        return self.boards

    def fetch_item(self, item_name):
        """
        Fetch the recent activity for item_name - current possible options:
        
        cards
        boards
        lists
        comments

        TODO: Maybe store the item as a class attribute instead of just
        returning it?

        """
        
        if item_name not in self.items:
            raise InvalidItem("%s is not a supported item." % item_name)

        for item in self.items:
            if item_name == item:
                return self.get_activity(self.items[item], self.get_boards())

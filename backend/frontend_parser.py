import pydantic


class FrontendState(pydantic.BaseModel):
    '''
    Schema for the React state of a client's frontend
    '''
    pass


class FrontendParser:
    '''
    Parses a Game object into a FrontendState to be given to a user's React frontend
    '''
    pass

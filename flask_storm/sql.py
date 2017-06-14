from storm.databases.postgres import PostgresConnection
from storm.variables import Variable

try:
    import sqlparse
except ImportError:
    sqlparse = None

try:
    from psycopg2.extensions import adapt as psycopg2_adapt
except ImportError:
    psycopg2_adapt = None

from .utils import colored

__all__ = [
    "Adapter",
    "default_adapter",
    "replace_placeholders",
    "format",
    "color",
]

class Adapter(object):
    def __init__(self, conn=None):
        self._conn = conn

    @property
    def type(self):
        if isinstance(self._conn, PostgresConnection):
            return "postgres"

    def _default_adapt(self, value):
        if isinstance(value, (str, unicode)):
            return "'{}'".format(value.replace("'", "''").replace("\\", "\\\\"))
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif value is None:
            return "NULL"
        elif isinstance(value, (int, long, float)):
            return str(value)
        else:
            return self._default_adapt(str(value))

    def adapt(self, value):
        if isinstance(value, Variable):
            value = value.get(to_db=True)

        if self.type == "postgres":
            output = psycopg2_adapt(value)
            if hasattr(output, "prepare"):
                output.prepare(self._conn._raw_connection)
            return output.getquoted()

        return self._default_adapt(value)


default_adapter = Adapter()


def replace_placeholders(statement, params, adapter=None):
    if adapter is None:
        adapter = default_adapter

    param_iter = (adapter.adapt(param) for param in params)
    tokens = []
    try:
        for token in sqlparse.parse(statement)[0].flatten():
            if str(token.ttype) == "Token.Name.Placeholder":
                tokens.append(param_iter.next())
            else:
                tokens.append(token.value)
    except StopIteration:
        raise ValueError("Not enough parameters provided")

    return "".join(tokens)


def format(statement):
    # If sqlparse is not installed it is not possible to do fancy formatting
    if sqlparse is None:
        return statement

    # To finish of we pretty print the output
    return sqlparse.format(
        statement,
        keyword_case="upper",
        identifier_case="lower",
        reindent=True,
        indent_tabs=False,
        indent_width=4)


def _color_token(token):
    Token = sqlparse.tokens
    if token.is_keyword or token.ttype is Token.Wildcard:
        return colored(token.value, 160, bold=True)
    elif token.ttype is Token.Punctuation:
        return colored(token.value, 246)
    elif isinstance(token, sqlparse.sql.Identifier):
        return colored(token.value, 69)
    elif token.ttype in Token.Literal.String:
        return colored(token.value, 220)
    elif token.ttype in Token.Literal.Number:
        return colored(token.value, 39)
    elif token.ttype in Token.Operator:
        return colored(token.value, 154)
    elif token.is_group:
        return "".join(_color_token(t) for t in token.tokens)
    return token.value


def color(statement):
    if sqlparse is None:
        return statement
    return "".join(_color_token(t) for t in sqlparse.parse(statement)[0].tokens)

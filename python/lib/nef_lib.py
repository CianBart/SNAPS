from argparse import Namespace
from typing import Iterator, Union, Dict

from pandas import DataFrame
from pynmrstar import Loop

from lib.util import is_int, is_float

NEF_TRUE = "true"
NEF_FALSE = "false"
NEF_CATEGORY_ATTR = "__NEF_CATEGORY__"

def loop_row_dict_iter(
    loop: Loop, convert: bool = True
) -> Iterator[Dict[str, Union[str, int, float]]]:
    """
    create an iterator that loops over the rows in a star file Loop as dictionaries, by default sensible
    conversions from strings to ints and floats are made
    :param loop: the Loop
    :param convert: try to convert values to ints or floats if possible [default is True]
    :return: iterator of rows as dictionaries
    """

    if not isinstance(loop, Loop):
        msg = f"""\
            loop must be of type Loop you provided a {loop.__class__.__name__}"
            value: {loop}
        """
        raise Exception(msg)

    for row in loop:
        row = {tag: value for tag, value in zip(loop.tags, row)}

        if convert:
            for key in row:
                row[key] = do_reasonable_type_conversions(row[key])

        yield row


def do_reasonable_type_conversions(value: str) -> Union[str, float, int]:
    """
    do reasonable type conversion from str to int or float
    :param value: the string to convert
    :return: value converted from str to int or float if possible
    """
    if is_int(value):
        value = int(value)
    elif is_float(value):
        value = float(value)
    elif value.lower() == NEF_FALSE:
        value = False
    elif value.lower() == NEF_TRUE:
        value = True
    return value

def loop_row_namespace_iter(loop: Loop, convert: bool = True) -> Iterator[Namespace]:
    """
    create an iterator that loops over the rows in a star file Loop as Namespaces, by default sensible
    conversions from strings to ints and floats are made
    :param loop: thr Loop
    :param convert: try to convert values to ints or floats if possible [default is True]
    :return: iterator of rows as dictionaries
    """
    for row in loop_row_dict_iter(loop, convert=convert):
        yield Namespace(**row)



def loop_to_dataframe(loop: Loop) -> DataFrame:
    """
    convert a pynmrstar Loop to a pandas DataFrame. Note the Loop category is
    saved in the dataframe's attrs['__NEF_CATEGORY__']

    :param loop: the pynmrstar Loop
    :return: a pandas DataFrame
    """
    tags = loop.tags
    data = DataFrame()

    # note this strips the preceding _
    data.attrs[NEF_CATEGORY_ATTR] = loop.category[1:]

    for tag in tags:
        if tag != "index":
            data[tag] = loop.get_tag(tag)

    return data


def dataframe_to_loop(frame: DataFrame, category: str = None) -> Loop:
    """
    convert a pandas DataFrame to a pynmrstar Loop

    :param frame: the pandas DataFrame
    :param category: the star category note this will override any category stored in attrs
    :return: the new pynmrstar Loop
    """
    loop = Loop.from_scratch(category=category)
    loop_data = {}
    for column in frame.columns:
        loop.add_tag(column)
        loop_data[column] = list(frame[column])

    loop.add_data(loop_data)

    if NEF_CATEGORY_ATTR in frame.attrs and not category:
        loop.set_category(frame.attrs[NEF_CATEGORY_ATTR])
    elif category:
        loop.set_category(category)

    return loop
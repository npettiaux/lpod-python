# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from lpod
from element import register_element_class, odf_element, odf_create_element
from element import FIRST_CHILD, PREV_SIBLING, NEXT_SIBLING
from paragraph import odf_create_paragraph
from utils import _get_element_list, _get_element


def odf_create_list_item(text_or_element=None):
    """Create a list item element.

    Sending a unicode text is just a shortcut for the most common case. To
    create a list item with several paragraphs or anything else (except
    tables), first create an empty list item, and fill it using the other
    "odf_create_*" functions.

    Arguments:

        text -- unicode or odf_element

    Return: odf_element
    """
    element = odf_create_element('<text:list-item/>')
    if type(text_or_element) is unicode:
        element.set_text_content(text_or_element)
    elif isinstance(text_or_element, odf_element):
        element.append_element(text_or_element)
    elif text_or_element is not None:
        raise TypeError, "expected unicode or odf_element"
    return element



def odf_create_list(text=[], style=None):
    """Create a list element.

    Arguments:

        text -- a list of unicode

        style -- unicode

    The "text" argument is just a shortcut for the most common case. To create
    complex lists, first create an empty list, and fill it using built list
    items.

    Return: odf_element
    """
    element = odf_create_element('<text:list/>')
    for value in text:
        element.append_element(odf_create_list_item(text_or_element=value))
    if style is not None:
        element.set_attribute('text:style-name', style)
    return element



class odf_list(odf_element):
    """Specialised element for lists.
    """

    def get_item_list(self, regex=None):
        return _get_element_list(self, 'text:list-item', regex=regex)


    def get_item_by_position(self, position):
        return _get_element(self, 'text:list-item', position=position)


    def get_item_by_content(self, regex):
        query = 'descendant::text:list-item/text:p'
        paragraphs = [p for p in self.get_element_list(query)
                      if p.match(regex)]
        if paragraphs:
            return paragraphs[0].get_parent()
        return None


    def set_header(self, text_or_element):
        if not isinstance(text_or_element, (list, tuple)):
            text_or_element = [text_or_element]
        # Remove existing header
        for element in self.get_element_list('text:p'):
            self.delete(element)
        for paragraph in reversed(text_or_element):
            if type(paragraph) is unicode:
                paragraph = odf_create_paragraph(paragraph)
            self.insert_element(paragraph, FIRST_CHILD)


    def insert_item(self, item, position=None, before=None, after=None):
        # Check if the item is already a list-item
        tag_name = item.get_name() if isinstance(item, odf_element) else None
        if tag_name != 'text:list-item':
            item = odf_create_list_item(item)

        if before is not None:
            before.insert_element(item, xmlposition=PREV_SIBLING)
        elif after is not None:
            after.insert_element(item, xmlposition=NEXT_SIBLING)
        elif position is not None:
            self.insert_element(item, position=position)
        else:
            raise ValueError, "position must be defined"


    def append_item(self, item):
        # Check if the item is already a list-item
        tag_name = item.get_name() if isinstance(item, odf_element) else None
        if tag_name != 'text:list-item':
            item = odf_create_list_item(item)
        self.append_element(item)


    def get_formated_text(self, context):
        result = []
        for list_item in self.get_element_list('text:list-item'):
            text = []
            for children in list_item.get_children():
                text.append(children.get_formated_text(context))
            text = u''.join(text)
            text = text.strip('\n')
            # Indent the text
            text = u'- %s\n' % text.replace(u'\n', u'\n  ')
            result.append(text)
        return u''.join(result)



register_element_class('text:list', odf_list)

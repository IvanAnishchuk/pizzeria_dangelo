"""
Custom pagination class to be used with 128-bit primary keys.

Theoretically is pretty powerful even if not quite polished yet.
Still, it does much good in just 100+ SLOC.
Note that base64url encoding used here does not preserve ordering, but given
that we use it only for transmission and never comparison it should be ok. For
generating sortable encoded tokens, use a custom alphabet (- < 0, Z < _ < a).
"""
import base64
import collections
import math
import typing
import uuid

import rest_framework.pagination
import rest_framework.request
import rest_framework.response
import rest_framework.settings


class IDPagination(rest_framework.pagination.CursorPagination):
    """
    Slightly customized cursor pagination.

    Works nicely with uids. And by utilizing offset could be made to work with
    any incompatible ordering not worse than offset+limit pagination. Not sure
    how easily such flexibility could be implemented, it's not needed right now.
    To make it completely universal, we also need to get the total item count
    (which would make it about as effective as normal page number or similar
    offset+limit). I think such potential universality is nice even if I don't
    use all the features right now. I'm not ashamed of this code and it kinda
    works, leaving it medium-rare for now so I can focus on the actual task.
    """
    cursor_query_param = 'cursor'
    default_page_size = rest_framework.settings.api_settings.PAGE_SIZE
    page_size = default_page_size  # configurable with cursor
    max_page_size = 1000  # 16-bit signed int is the encoding limit
    ordering = '-uid'  # NOTE: ordering will likely break in early 2100s
    position_first = b'\x00' * 16
    position_last = b'\xff' * 16
    # NOTE: superclass sets offset_cutoff = 1000

    def decode_cursor(
            self,
            request: rest_framework.request.Request,
    ) -> rest_framework.pagination.Cursor:
        """
        Decode 16+ bytes of base64url-encoded cursor.

        Set page size and return position, direction, and offset.
        (As Cursor object.)
        """
        # we might need to change Cursor class at some point
        encoded = request.query_params.get(self.cursor_query_param)
        if encoded is None:
            return None
        try:
            missing_padding = len(encoded) % 4
            decoded = base64.urlsafe_b64decode(
                encoded.encode('ascii') + b'=' * (4 - missing_padding),
            )
            # Position is uuid consisting of first 14 input bytes and two nulls
            position_bytes = decoded[:14] + b'\0\0'
            # Limit (page size) is the next two bytes (signed int)
            # Special cases are 0 and +1 or -1
            limit_bytes = decoded[14:16]
            # Offset is anything beyond that (0+ bytes unsigned int)
            offset_bytes = decoded[16:]
            if offset_bytes:
                offset = int.from_bytes(offset_bytes, 'big')
            else:
                offset = 0
            # DRF uses a private function for this but we can simplify
            offset = min(offset, self.offset_cutoff)

            limit = int.from_bytes(limit_bytes, 'big', signed=True)
            reverse = limit < 0

            limit = abs(limit) - 1
            if not limit:  # zero means one page
                limit = self.default_page_size
            self.page_size = min(limit, self.max_page_size)

            if position_bytes == self.position_first:
                position = None
            else:
                position = uuid.UUID(bytes=position_bytes)
        except (TypeError, ValueError):
            raise rest_framework.exceptions.NotFound(self.invalid_cursor_message)
        return rest_framework.pagination.Cursor(offset, reverse, position)

    def encode_cursor(self, cursor: rest_framework.pagination.Cursor) -> str:
        """
        Simple and effective cursor packing.

        First 16 bytes for ID, page size and direction, then 0+ bytes for offset.
        DRF's cursor encoding is surprisingly ineffective with UUID keys, and
        otherwise. This usually results in 16 bytes encoded into 22 (base64url)
        while even for shorter keys (like second-resolution timestamp) DRF
        returns 25 bytes or longer (with silly percent-escaping because they
        used the wrong base64 variant and forgot to strip the padding).
        Even with some offset added (usually a couple bytes + base64 overhead)
        this version is shorter than most alternatives.
        Additionally, a little bit of binary obscurity helps frontend developers
        understand that they are not supposed to edit parameters (while keeping
        them essentially as flexible as with other methods).
        """
        (offset, reverse, position) = cursor
        if position is None:
            position = self.position_first
        elif not isinstance(position, uuid.UUID):
            position = uuid.UUID(position).bytes
        else:
            position = position.bytes
        # Passing page size in an attribute is not ideal, but I don't wanna
        # change cursor objects as that would require many other changes
        limit = self.page_size
        limit += 1  # we can't use signed zeros, so we adjust the value here
        # This actually nicely aligns with how the paginator paginates, when
        # you request 50 elements it actually retrieves 51 to determine the
        # next position. And special cases of +1 and -1 could be interpreted
        # as "one page" rather than one element.
        if reverse:
            # We can pack page size up to ~32k and forward/backward direction
            # into two bytes (that are part of 16 uuid bytes) - efficiency!
            limit *= -1
        # encoding offset as a variable-length byte sequence (shouldn't be
        # longer than a couple bytes with default settings, most cases
        # is only zero to one byte)
        limit = limit.to_bytes(2, 'big', signed=True)
        if offset == 0:
            # If offset is zero, don't add anything
            offset = b''
        else:
            # Otherwise encode into arbitrary-length byte sequence
            offset = offset.to_bytes(
                math.ceil(offset.bit_length() / 8),
                'big',
                signed=True,
            )
        encoded = (
            base64
            .urlsafe_b64encode(position[:14] + limit + offset)
            .decode('ascii')
            .rstrip('=')
        )
        # I don't like using a query param for this but I haven't figured out
        # any good alternative way and this was used by DRF for years.
        return rest_framework.pagination.replace_query_param(
            self.base_url, self.cursor_query_param, encoded,
        )

    def get_paginated_response(self, data: list) -> rest_framework.response.Response:
        """
        Inspired by drf-link-header-pagination (but rewritten from scratch)

        It is a good library if you only need page-number pagination but
        for my needs depending on it and subclassing pagination class only
        to override this method would be pointless (the library doesn't
        provide much other code).
        """
        links = []
        for condition, getter, label in (
                (self.has_previous, self.get_first_link, 'first'),
                (self.has_previous, self.get_previous_link, 'prev'),
                (self.has_next, self.get_next_link, 'next'),
                # last_link could be here
        ):
            if condition:
                links.append('<{0}>; rel="{1}"'.format(getter(), label))

        # Any extra links could be added here

        headers = {'Link': ', '.join(links)} if links else {}

        # This is a nice place to inject additional headers like Content-Range

        return rest_framework.response.Response(data, headers=headers)

    def get_first_link(self) -> typing.Union[str, None]:
        """
        Get page one.

        Rather than stripping the cursor entirely this adds a special cursor
        starting at zero (uuid corresponding to 16 null bytes) but with page
        size set. I like it this way.
        """
        if not self.has_previous:
            return None
        return self.encode_cursor(rest_framework.pagination.Cursor(
            offset=0,
            reverse=False,
            position=uuid.UUID(bytes=self.position_first),
        ))

    def get_last_link(self) -> typing.Optional[str]:  # pylint: disable=no-self-use
        """
        Get the last page.

        Additional nicety: for the default page size the two last bytes of
        uuid would look like 'b'\xff\xff' (-1) giving us 16 b'\xff' bytes and
        the resulting base64 token looking like '_____________________w'
        which, I think, looks good together with the first zero-position token
        'AAAAAAAAAAAAAAAAAAAAAQ' (last couple bytes can vary for different page
        sizes and like, this can also change with encoding).
        While theoretically possible and sound, this doesn't work right now
        and needs review and fixing :( still, DRF's cursor pagination can't do
        it either by default.
        """
        return None  # Doesn't work, needs investigation

    def get_html_context(self) -> typing.Dict[str, typing.Optional[str]]:
        return collections.OrderedDict([
            ('first_url', self.get_first_link()),
            ('previous_url', self.get_previous_link()),
            ('next_url', self.get_next_link()),
            # last_url could be here
        ])

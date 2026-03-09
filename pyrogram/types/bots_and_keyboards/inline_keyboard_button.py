#  Pyrofork - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#  Copyright (C) 2022-present Mayuri-Chan <https://github.com/Mayuri-Chan>
#
#  This file is part of Pyrofork.
#
#  Pyrofork is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrofork is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrofork.  If not, see <http://www.gnu.org/licenses/>.

# DESTINATION: pyrogram/types/bots_and_keyboards/inline_keyboard_button.py

from typing import Union, Optional

import pyrogram
from pyrogram import enums, raw
from pyrogram import types
from ..object import Object


# Maps each InlineButtonTheme value → the matching flag name on KeyboardButtonStyle
_THEME_TO_FLAG: dict = {
    enums.InlineButtonTheme.PRIMARY: "bg_primary",
    enums.InlineButtonTheme.DANGER:  "bg_danger",
    enums.InlineButtonTheme.SUCCESS: "bg_success",
}

# Reverse: flag name on KeyboardButtonStyle → InlineButtonTheme value
_FLAG_TO_THEME: dict = {v: k for k, v in _THEME_TO_FLAG.items()}


def _build_appearance(
    theme: Optional["enums.InlineButtonTheme"],
    icon_custom_emoji_id: Optional[int]
) -> Optional["raw.types.KeyboardButtonStyle"]:
    """Convert high-level theme + emoji ID into a raw ``KeyboardButtonStyle``.

    Returns ``None`` when nothing is set, which leaves the button default.
    """
    if theme is None and icon_custom_emoji_id is None:
        return None

    flags = {flag: (theme == t) or None for t, flag in _THEME_TO_FLAG.items()}
    return raw.types.KeyboardButtonStyle(**flags, icon=icon_custom_emoji_id)


def _parse_appearance(raw_style) -> tuple:
    """Unpack a raw ``KeyboardButtonStyle`` into ``(InlineButtonTheme, emoji_id)``.

    Returns ``(None, None)`` when the style object is absent.
    """
    if raw_style is None:
        return None, None

    matched_theme = next(
        (theme for flag, theme in _FLAG_TO_THEME.items() if getattr(raw_style, flag, False)),
        None
    )
    return matched_theme, getattr(raw_style, "icon", None)


class InlineKeyboardButton(Object):
    """One button of an inline keyboard.

    You must use exactly one of the optional action fields.

    Parameters:
        text (``str``):
            Label text on the button.

        callback_data (``str`` | ``bytes``, *optional*):
            Data to be sent in a callback query to the bot when the button is
            pressed, 1-64 bytes.

        url (``str``, *optional*):
            HTTP url to be opened when button is pressed.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            Description of the Web App that will be launched when the user
            presses the button. Available only in private chats between a
            user and the bot.

        login_url (:obj:`~pyrogram.types.LoginUrl`, *optional*):
            An HTTP URL used to automatically authorize the user via the
            Telegram Login Widget.

        user_id (``int``, *optional*):
            User id, for links to the user profile.

        switch_inline_query (``str``, *optional*):
            Prompt the user to select one of their chats and insert the
            bot's username and specified inline query in the input field.

        switch_inline_query_current_chat (``str``, *optional*):
            Insert the bot's username and the specified inline query in the
            current chat's input field.

        callback_game (:obj:`~pyrogram.types.CallbackGame`, *optional*):
            Launch the game attached to the message.
            **NOTE**: Must always be the first button in the first row.

        requires_password (``bool``, *optional*):
            Request the user's 2-step verification password before sending
            the callback query.

        copy_text (``str``, *optional*):
            Text copied to the clipboard when the button is pressed.

        theme (:obj:`~pyrogram.enums.InlineButtonTheme`, *optional*):
            Colour theme for the button background.
            One of :obj:`~pyrogram.enums.InlineButtonTheme.PRIMARY` (blue),
            :obj:`~pyrogram.enums.InlineButtonTheme.DANGER` (red), or
            :obj:`~pyrogram.enums.InlineButtonTheme.SUCCESS` (green).

        icon_custom_emoji_id (``int``, *optional*):
            Unique identifier of the custom emoji shown before the button
            text. Matches the official Telegram Bot API 9.4 field name.
            Only works if the bot owner has a Telegram Premium subscription.
    """

    def __init__(
        self,
        text: str,
        callback_data: Optional[Union[str, bytes]] = None,
        url: Optional[str] = None,
        web_app: Optional["types.WebAppInfo"] = None,
        login_url: Optional["types.LoginUrl"] = None,
        user_id: Optional[int] = None,
        switch_inline_query: Optional[str] = None,
        switch_inline_query_current_chat: Optional[str] = None,
        callback_game: Optional["types.CallbackGame"] = None,
        requires_password: Optional[bool] = None,
        copy_text: Optional[str] = None,
        theme: Optional["enums.InlineButtonTheme"] = None,
        icon_custom_emoji_id: Optional[int] = None,
    ):
        super().__init__()

        self.text = str(text)
        self.callback_data = callback_data
        self.url = url
        self.web_app = web_app
        self.login_url = login_url
        self.user_id = user_id
        self.switch_inline_query = switch_inline_query
        self.switch_inline_query_current_chat = switch_inline_query_current_chat
        self.callback_game = callback_game
        self.requires_password = requires_password
        self.copy_text = copy_text
        self.theme = theme
        self.icon_custom_emoji_id = int(icon_custom_emoji_id) if icon_custom_emoji_id is not None else None

    @staticmethod
    def read(b: "raw.base.KeyboardButton"):
        if isinstance(b, raw.types.KeyboardButtonCallback):
            try:
                data = b.data.decode()
            except UnicodeDecodeError:
                data = b.data

            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return InlineKeyboardButton(
                text=b.text,
                callback_data=data,
                requires_password=getattr(b, "requires_password", None),
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonUrl):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return InlineKeyboardButton(
                text=b.text,
                url=b.url,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonUrlAuth):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return InlineKeyboardButton(
                text=b.text,
                login_url=types.LoginUrl.read(b),
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonUserProfile):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return InlineKeyboardButton(
                text=b.text,
                user_id=b.user_id,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonSwitchInline):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            if b.same_peer:
                return InlineKeyboardButton(
                    text=b.text,
                    switch_inline_query_current_chat=b.query,
                    theme=theme,
                    icon_custom_emoji_id=emoji_id
                )
            return InlineKeyboardButton(
                text=b.text,
                switch_inline_query=b.query,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonGame):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return InlineKeyboardButton(
                text=b.text,
                callback_game=types.CallbackGame(),
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonWebView):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return InlineKeyboardButton(
                text=b.text,
                web_app=types.WebAppInfo(url=b.url),
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonCopy):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return types.InlineKeyboardButton(
                text=b.text,
                copy_text=b.copy_text,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonBuy):
            return types.InlineKeyboardButtonBuy.read(b)

    async def write(self, client: "pyrogram.Client"):
        appearance = _build_appearance(self.theme, self.icon_custom_emoji_id)

        if self.callback_data is not None:
            data = (
                bytes(self.callback_data, "utf-8")
                if isinstance(self.callback_data, str)
                else self.callback_data
            )
            return raw.types.KeyboardButtonCallback(
                text=self.text,
                data=data,
                requires_password=self.requires_password,
                style=appearance
            )

        if self.url is not None:
            return raw.types.KeyboardButtonUrl(
                text=self.text,
                url=self.url,
                style=appearance
            )

        if self.login_url is not None:
            return self.login_url.write(
                text=self.text,
                bot=await client.resolve_peer(self.login_url.bot_username or "self")
            )

        if self.user_id is not None:
            return raw.types.InputKeyboardButtonUserProfile(
                text=self.text,
                user_id=await client.resolve_peer(self.user_id),
                style=appearance
            )

        if self.switch_inline_query is not None:
            return raw.types.KeyboardButtonSwitchInline(
                text=self.text,
                query=self.switch_inline_query,
                style=appearance
            )

        if self.switch_inline_query_current_chat is not None:
            return raw.types.KeyboardButtonSwitchInline(
                text=self.text,
                query=self.switch_inline_query_current_chat,
                same_peer=True,
                style=appearance
            )

        if self.callback_game is not None:
            return raw.types.KeyboardButtonGame(
                text=self.text,
                style=appearance
            )

        if self.web_app is not None:
            return raw.types.KeyboardButtonWebView(
                text=self.text,
                url=self.web_app.url,
                style=appearance
            )

        if self.copy_text is not None:
            return raw.types.KeyboardButtonCopy(
                text=self.text,
                copy_text=self.copy_text,
                style=appearance
            )

        return raw.types.KeyboardButton(
            text=self.text,
            style=appearance
        )

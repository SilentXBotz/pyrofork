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

# DESTINATION: pyrogram/types/bots_and_keyboards/keyboard_button.py

from typing import Optional, Union

from pyrogram import enums, raw, types
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
    if theme is None and icon_custom_emoji_id is None:
        return None
    flags = {flag: (theme == t) or None for t, flag in _THEME_TO_FLAG.items()}
    return raw.types.KeyboardButtonStyle(**flags, icon=icon_custom_emoji_id)


def _parse_appearance(raw_style) -> tuple:
    if raw_style is None:
        return None, None
    matched_theme = next(
        (theme for flag, theme in _FLAG_TO_THEME.items() if getattr(raw_style, flag, False)),
        None
    )
    return matched_theme, getattr(raw_style, "icon", None)


class KeyboardButton(Object):
    """One button of the reply keyboard.

    For simple text buttons a plain ``str`` can be used instead of this
    object to specify the button text. Optional fields are mutually exclusive.

    Parameters:
        text (``str``):
            Text of the button. If none of the optional fields are used it
            will be sent as a message when the button is pressed.

        request_contact (``bool``, *optional*):
            If ``True``, the user's phone number will be sent as a contact
            when the button is pressed. Available in private chats only.

        request_location (``bool``, *optional*):
            If ``True``, the user's current location will be sent when the
            button is pressed. Available in private chats only.

        request_chat (:obj:`~pyrogram.types.RequestPeerTypeChannel` | :obj:`~pyrogram.types.RequestPeerTypeChat`, *optional*):
            Criteria used to request a suitable chat or channel.

        request_user (:obj:`~pyrogram.types.RequestPeerTypeUser`, *optional*):
            Criteria used to request a suitable user.

        web_app (:obj:`~pyrogram.types.WebAppInfo`, *optional*):
            The Web App that will be launched when the button is pressed.

        copy_text (``str``, *optional*):
            Text copied to the clipboard when the button is pressed.

        request_poll (:obj:`~pyrogram.enums.PollType`, *optional*):
            Ask the user to create a poll.

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
        request_contact: bool = None,
        request_location: bool = None,
        request_chat: Union["types.RequestPeerTypeChat", "types.RequestPeerTypeChannel"] = None,
        request_user: "types.RequestPeerTypeUser" = None,
        web_app: "types.WebAppInfo" = None,
        copy_text: Optional[str] = None,
        request_poll: Optional["enums.PollType"] = None,
        theme: Optional["enums.InlineButtonTheme"] = None,
        icon_custom_emoji_id: Optional[int] = None,
    ):
        super().__init__()

        self.text = str(text)
        self.request_contact = request_contact
        self.request_location = request_location
        self.request_chat = request_chat
        self.request_user = request_user
        self.web_app = web_app
        self.copy_text = copy_text
        self.request_poll = request_poll
        self.theme = theme
        self.icon_custom_emoji_id = int(icon_custom_emoji_id) if icon_custom_emoji_id is not None else None

    @staticmethod
    def read(b):
        if isinstance(b, raw.types.KeyboardButton):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            if theme is None and emoji_id is None:
                return b.text
            return KeyboardButton(text=b.text, theme=theme, icon_custom_emoji_id=emoji_id)

        if isinstance(b, raw.types.KeyboardButtonRequestPhone):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return KeyboardButton(
                text=b.text,
                request_contact=True,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonRequestGeoLocation):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return KeyboardButton(
                text=b.text,
                request_location=True,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonSimpleWebView):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return KeyboardButton(
                text=b.text,
                web_app=types.WebAppInfo(url=b.url),
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonCopy):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            return KeyboardButton(
                text=b.text,
                copy_text=b.copy_text,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonRequestPoll):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))
            quiz = getattr(b, "quiz", None)
            if quiz is True:
                poll_type = enums.PollType.QUIZ
            elif quiz is False:
                poll_type = enums.PollType.REGULAR
            else:
                poll_type = None
            return KeyboardButton(
                text=b.text,
                request_poll=poll_type,
                theme=theme,
                icon_custom_emoji_id=emoji_id
            )

        if isinstance(b, raw.types.KeyboardButtonRequestPeer):
            theme, emoji_id = _parse_appearance(getattr(b, "style", None))

            if isinstance(b.peer_type, raw.types.RequestPeerTypeBroadcast):
                user_privileges = getattr(b.peer_type, "user_admin_rights", None)
                bot_privileges = getattr(b.peer_type, "bot_admin_rights", None)
                return KeyboardButton(
                    text=b.text,
                    request_chat=types.RequestPeerTypeChannel(
                        is_creator=b.peer_type.creator,
                        is_username=b.peer_type.has_username,
                        max=b.max_quantity,
                        user_privileges=user_privileges,
                        bot_privileges=bot_privileges
                    ),
                    theme=theme,
                    icon_custom_emoji_id=emoji_id
                )

            if isinstance(b.peer_type, raw.types.RequestPeerTypeChat):
                user_privileges = getattr(b.peer_type, "user_admin_rights", None)
                bot_privileges = getattr(b.peer_type, "bot_admin_rights", None)
                return KeyboardButton(
                    text=b.text,
                    request_chat=types.RequestPeerTypeChat(
                        is_creator=b.peer_type.creator,
                        is_bot_participant=b.peer_type.bot_participant,
                        is_username=b.peer_type.has_username,
                        is_forum=b.peer_type.forum,
                        max=b.max_quantity,
                        user_privileges=user_privileges,
                        bot_privileges=bot_privileges
                    ),
                    theme=theme,
                    icon_custom_emoji_id=emoji_id
                )

            if isinstance(b.peer_type, raw.types.RequestPeerTypeUser):
                return KeyboardButton(
                    text=b.text,
                    request_user=types.RequestPeerTypeUser(
                        is_bot=b.peer_type.bot,
                        is_premium=b.peer_type.premium,
                        max=b.max_quantity
                    ),
                    theme=theme,
                    icon_custom_emoji_id=emoji_id
                )

    def write(self):
        appearance = _build_appearance(self.theme, self.icon_custom_emoji_id)

        if self.request_contact:
            return raw.types.KeyboardButtonRequestPhone(
                text=self.text,
                style=appearance
            )

        if self.request_location:
            return raw.types.KeyboardButtonRequestGeoLocation(
                text=self.text,
                style=appearance
            )

        if self.copy_text is not None:
            return raw.types.KeyboardButtonCopy(
                text=self.text,
                copy_text=self.copy_text,
                style=appearance
            )

        if self.request_poll is not None:
            if self.request_poll == enums.PollType.QUIZ:
                quiz = True
            elif self.request_poll == enums.PollType.REGULAR:
                quiz = False
            else:
                quiz = None
            return raw.types.KeyboardButtonRequestPoll(
                text=self.text,
                quiz=quiz,
                style=appearance
            )

        if self.request_chat:
            user_privileges = self.request_chat.user_privileges
            bot_privileges = self.request_chat.bot_privileges

            user_admin_rights = raw.types.ChatAdminRights(
                change_info=user_privileges.can_change_info,
                post_messages=user_privileges.can_post_messages,
                post_stories=user_privileges.can_post_stories,
                edit_messages=user_privileges.can_edit_messages,
                edit_stories=user_privileges.can_post_stories,
                delete_messages=user_privileges.can_delete_messages,
                delete_stories=user_privileges.can_delete_stories,
                ban_users=user_privileges.can_restrict_members,
                invite_users=user_privileges.can_invite_users,
                pin_messages=user_privileges.can_pin_messages,
                add_admins=user_privileges.can_promote_members,
                anonymous=user_privileges.is_anonymous,
                manage_call=user_privileges.can_manage_video_chats,
                other=user_privileges.can_manage_chat
            ) if user_privileges else None

            bot_admin_rights = raw.types.ChatAdminRights(
                change_info=bot_privileges.can_change_info,
                post_messages=bot_privileges.can_post_messages,
                post_stories=bot_privileges.can_post_stories,
                edit_messages=bot_privileges.can_edit_messages,
                edit_stories=bot_privileges.can_post_stories,
                delete_messages=bot_privileges.can_delete_messages,
                delete_stories=bot_privileges.can_delete_stories,
                ban_users=bot_privileges.can_restrict_members,
                invite_users=bot_privileges.can_invite_users,
                pin_messages=bot_privileges.can_pin_messages,
                add_admins=bot_privileges.can_promote_members,
                anonymous=bot_privileges.is_anonymous,
                manage_call=bot_privileges.can_manage_video_chats,
                other=bot_privileges.can_manage_chat
            ) if bot_privileges else None

            if isinstance(self.request_chat, types.RequestPeerTypeChannel):
                return raw.types.InputKeyboardButtonRequestPeer(
                    text=self.text,
                    button_id=self.request_chat.button_id,
                    peer_type=raw.types.RequestPeerTypeBroadcast(
                        creator=self.request_chat.is_creator,
                        has_username=self.request_chat.is_username,
                        user_admin_rights=user_admin_rights,
                        bot_admin_rights=bot_admin_rights
                    ),
                    max_quantity=self.request_chat.max,
                    name_requested=self.request_chat.is_name_requested,
                    username_requested=self.request_chat.is_username_requested,
                    photo_requested=self.request_chat.is_photo_requested,
                    style=appearance
                )

            return raw.types.InputKeyboardButtonRequestPeer(
                text=self.text,
                button_id=self.request_chat.button_id,
                peer_type=raw.types.RequestPeerTypeChat(
                    creator=self.request_chat.is_creator,
                    bot_participant=self.request_chat.is_bot_participant,
                    has_username=self.request_chat.is_username,
                    forum=self.request_chat.is_forum,
                    user_admin_rights=user_admin_rights,
                    bot_admin_rights=bot_admin_rights
                ),
                max_quantity=self.request_chat.max,
                name_requested=self.request_chat.is_name_requested,
                username_requested=self.request_chat.is_username_requested,
                photo_requested=self.request_chat.is_photo_requested,
                style=appearance
            )

        if self.request_user:
            return raw.types.InputKeyboardButtonRequestPeer(
                text=self.text,
                button_id=self.request_user.button_id,
                peer_type=raw.types.RequestPeerTypeUser(
                    bot=self.request_user.is_bot,
                    premium=self.request_user.is_premium
                ),
                max_quantity=self.request_user.max,
                name_requested=self.request_user.is_name_requested,
                username_requested=self.request_user.is_username_requested,
                photo_requested=self.request_user.is_photo_requested,
                style=appearance
            )

        if self.web_app:
            return raw.types.KeyboardButtonSimpleWebView(
                text=self.text,
                url=self.web_app.url,
                style=appearance
            )

        return raw.types.KeyboardButton(text=self.text, style=appearance)

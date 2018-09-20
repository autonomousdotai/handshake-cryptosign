#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
import app.constants as CONST

from datetime import datetime
from app.helpers.utils import render_unsubscribe_url
from app.constants import Handshake as HandshakeStatus

def render_email_subscribe_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        You’ve successfully made a prediction. Go you!<br/>
        We’ll email you the result, the minute it comes in.
        Enjoy daydreaming about all of the things you’ll (hopefully) do with your winnings.<br/>
        Stay cool.
        Ninja<br/>

        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_lose_free_bet_content(app, user_id, free_bet_available):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Not so lucky this time :( <br/>
        You have {} freebets <br/>
        But you know what we say... <br/>
        If at first you don’t succeed, try again for free.<br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_win_free_bet_content(app, user_id, free_bet_available):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        YOU WON! <br/>
        Wanna win more? <br/>
        Of course you do, who doesn’t!<br/>
        You have {} freebets <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_draw_free_bet_content(app, user_id, free_bet_available):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        So... it’s a DRAW. <br/>
        Wanna another shot at glory? <br/>
        You have {} freebets <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_not_match_free_bet_content(app, user_id, free_bet_available):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Unfortunately, this time you weren't matched. <br/>
        No worries, let’s have another go. <br/>
        You have {} freebets <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_lose_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Sorry, you lost :( <br/>
        You know what they say... <br/>
        "If at first you don’t succeed, try again for free."<br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_win_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        YOU WON! <br/>
        Congrats, you’ve successfully predicted the future.<br/>
        Wanna see if you can do it again? <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_draw_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        So... it’s a DRAW. <br/>
        Not to worry, there’s always next time. <br/>
        We believe in you! <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_not_match_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Unfortunately, this time you weren't matched. <br/>
        Luckily, you can always try again. <br/>
        Let’s do it!<br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_notify_result_content(app, user_id, address, outcome_name, match_name, outcome_result, bet_side, status, is_free_bet, free_bet_available):
    content = ""

    if is_free_bet and free_bet_available > 0:
        # if status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
        if status == HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']:
            content = render_email_not_match_free_bet_content(app, user_id, free_bet_available)
        else:
            if outcome_result == CONST.RESULT_TYPE["DRAW"]:
                content = render_email_draw_free_bet_content(app, user_id, free_bet_available)
            else:
                if outcome_result == bet_side:
                    content = render_email_win_free_bet_content(app, user_id, free_bet_available)
                else:
                    content = render_email_lose_free_bet_content(app, user_id, free_bet_available)
    else:
        if status == HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']:
            content = render_email_not_match_real_bet_content(app, user_id)
        else:
            if outcome_result == CONST.RESULT_TYPE["DRAW"]:
                content = render_email_draw_real_bet_content(app, user_id)
            else:
                if outcome_result == bet_side:
                    content = render_email_win_real_bet_content(app, user_id)
                else:
                    content = render_email_lose_real_bet_content(app, user_id)

    return content

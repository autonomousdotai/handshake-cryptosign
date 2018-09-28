#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
import app.constants as CONST

from datetime import datetime
from app.helpers.utils import render_unsubscribe_url
from app.constants import Handshake as HandshakeStatus

def render_email_subscribe_content(app_config, user_id):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        You’ve successfully made a prediction. Go you!<br/>
        We’ll email you the result, the minute it comes in.
        Enjoy daydreaming about all of the things you’ll (hopefully) do with your winnings.<br/>
        Stay cool.
        Ninja<br/>

        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_lose_free_bet_content(app_config, user_id, free_bet_available):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Not so lucky this time :( <br/>
        You have {} freebets <br/>
        But you know what we say... <br/>
        If at first you don’t succeed, try again for free.<br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_win_free_bet_content(app_config, user_id, free_bet_available):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        YOU WON! <br/>
        Wanna win more? <br/>
        Of course you do, who doesn’t!<br/>
        You have {} freebets <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_draw_free_bet_content(app_config, user_id, free_bet_available):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        So... it’s a DRAW. <br/>
        Wanna another shot at glory? <br/>
        You have {} freebets <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_not_match_free_bet_content(app_config, user_id, free_bet_available):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Unfortunately, this time you weren't matched. <br/>
        No worries, let’s have another go. <br/>
        You have {} freebets <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(free_bet_available, render_unsubscribe_url(user_id, passphase))

def render_email_lose_real_bet_content(app_config, user_id):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Sorry, you lost :( <br/>
        You know what they say... <br/>
        "If at first you don’t succeed, try again for free."<br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_win_real_bet_content(app_config, user_id):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        YOU WON! <br/>
        Congrats, you’ve successfully predicted the future.<br/>
        Wanna see if you can do it again? <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_draw_real_bet_content(app_config, user_id):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        So... it’s a DRAW. <br/>
        Not to worry, there’s always next time. <br/>
        We believe in you! <br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_not_match_real_bet_content(app_config, user_id):
    passphase = app_config["PASSPHASE"]
    return """
        Hey Ninja!<br/>
        Unfortunately, this time you weren't matched. <br/>
        Luckily, you can always try again. <br/>
        Let’s do it!<br/>
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))

def render_footer_email_content(app_config, user_id, free_bet_available):
    passphase = app_config["PASSPHASE"]
    html = ""

    if free_bet_available > 0:
        html = "You have {} freebets <br/>".format(free_bet_available)

    return html + """
        <a href="http://ninja.org/prediction">PLAY NOW</a><br/>
        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_notify_result_content(app_config, items, outcome_result, free_bet_available):
    content = "Hey Ninja!<br/>"
    
    counter_not_match = 0
    counter_draw = 0
    counter_win = 0
    counter_lose = 0

    for item in items:
        if item.free_bet == 1:
            # if status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
            if item.status == HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']:
                # content = render_email_not_match_free_bet_content(app_config, user_id, free_bet_available)
                counter_not_match += 1
            else:
                if outcome_result == CONST.RESULT_TYPE["DRAW"]:
                    counter_draw += 1
                    # content = render_email_draw_free_bet_content(app_config, user_id, free_bet_available)
                else:
                    if outcome_result == item.side:
                        counter_win += 1
                        # content = render_email_win_free_bet_content(app_config, user_id, free_bet_available)
                    else:
                        counter_lose += 1
                        # content = render_email_lose_free_bet_content(app_config, user_id, free_bet_available)
        else:
            if item.status == HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']:
                counter_not_match += 1
                # content = render_email_not_match_real_bet_content(app_config, user_id)
            else:
                if outcome_result == CONST.RESULT_TYPE["DRAW"]:
                    counter_draw += 1
                    # content = render_email_draw_real_bet_content(app_config, user_id)
                else:
                    if outcome_result == item.side:
                        counter_win += 1
                        # content = render_email_win_real_bet_content(app_config, user_id)
                    else:
                        counter_lose += 1
                        # content = render_email_lose_real_bet_content(app_config, user_id)

    if counter_not_match > 0:
        content += "Your have: {} bet not match<br/>".format(counter_not_match)
    if counter_draw > 0:
        content += "Your have: {} bet draw<br/>".format(counter_draw)
    if counter_win > 0:
        content += "Your have: {} bet win<br/>".format(counter_win)
    if counter_lose > 0:
        content += "Your have: {} bet lose<br/>".format(counter_lose)

    content += render_footer_email_content(app_config, items[0].user_id, free_bet_available)
    return content

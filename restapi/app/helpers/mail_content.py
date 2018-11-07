#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
import app.constants as CONST

from datetime import datetime
from app.helpers.utils import render_unsubscribe_url, second_to_strftime
from app.constants import Handshake as HandshakeStatus

def render_email_subscribe_content(passphase, match_id, user_id):
    return """
        Hey Ninja!<br/>
        You’ve successfully made a prediction. Go you!<br/>
        We’ll email you the result, the minute it comes in.
        Enjoy daydreaming about all of the things you’ll (hopefully) do with your winnings.<br/>
        Stay cool.
        Ninja<br/>

        <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
    """.format(render_unsubscribe_url(user_id, passphase))


def render_row_table_content(outcome_name, side, result):
    text = ""
    if result == "DRAW":
        text = "So... it’s a DRAW."
    elif result == "WIN":
        text = "You won! Please wait to withdraw your winnings."
    elif result == "LOSE":
        text = "You lost. Better luck next time."
    else:
        text = "Unfortunately, this time you weren't matched. "

    return """
    <tr>
        <td>{}</td>
        <td>{}</td>
        <td>{}</td>
    </tr>
    """.format(outcome_name, "Support" if side == 1 else "Oppose", text)


def render_email_notify_result_content(app_config, items, free_bet_available):
    content = """
    <html>
    <head>
    <style>
        #bet_result {
            font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%;
        }

        #bet_result td, #bet_result th {
            border: 1px solid #ddd;
            padding: 8px;
        }

        #bet_result tr:nth-child(even){background-color: #f2f2f2;}

        #bet_result tr:hover {background-color: #ddd;}

        #bet_result th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
        }
    </style>
    </head>
    <body>
    Hey Ninja!<br/>
    The results are in!<br/>
    Let’s see how you did?<br/>

    <table id="bet_result">
        <tr>
            <th>Outcome</th>
            <th>Side</th>
            <th>Result</th>
        </tr>
    """

    for bet in items:
        if bet.status != HandshakeStatus['STATUS_PENDING']:
            if bet.free_bet == 1:
                if bet.status == HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']:
                    content += render_row_table_content(bet.outcome_name, bet.side, "NOT_MATCH")
                else:
                    if bet.outcome_result == CONST.RESULT_TYPE["DRAW"]:
                        content += render_row_table_content(bet.outcome_name, bet.side, "DRAW")
                    else:
                        if bet.outcome_result == bet.side:
                            content += render_row_table_content(bet.outcome_name, bet.side, "WIN")
                        else:
                            content += render_row_table_content(bet.outcome_name, bet.side, "LOSE")
            else:
                if bet.status == HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']:
                    content += render_row_table_content(bet.outcome_name, bet.side, "NOT_MATCH")
                else:
                    if bet.outcome_result == CONST.RESULT_TYPE["DRAW"]:
                        content += render_row_table_content(bet.outcome_name, bet.side, "DRAW")
                    else:
                        if bet.outcome_result == bet.side:
                            content += render_row_table_content(bet.outcome_name, bet.side, "WIN")
                        else:
                            content += render_row_table_content(bet.outcome_name, bet.side, "LOSE")

    content += "</table>"

    if free_bet_available > 0:
        content += """Please go <a href="http://ninja.org/me">Ninja Prediction</a> on your mobile to claim them. <br/>"""

    content += """<a href="http://ninja.org/prediction">PLAY NOW</a><br/>"""

    content += "</body></html>"

    return content


def new_market_mail_content(match, link):
    closing_time = second_to_strftime(match.date) 
    report_time = second_to_strftime(match.reportTime)
    dispute_time = second_to_strftime(match.disputeTime)

    return """
        Hey Ninja,<br/><br/>
        Congrats! <br/>
        You’ve successfully created an event. <br/>
        Please review all your event info below: <br/>
        <div>
            <blockquote style="margin:0 0 0 40px;border:none;padding:0px">
                <div>
                    Event name: {}<br/>
                    When your event ends: {} (UTC)<br/>
                    Report event results before: {} (UTC)<br/>
                    Event closes (if there’s no dispute): {} (UTC)<br/>
                </div>
            </blockquote>
        </div>
        Tell your friends: <a href="http://ninja.org/prediction{}">ninja.org/prediction{}</a><br/>
        Good luck!<br/>
        <div>
            <img src="https://d2q7nqismduvva.cloudfront.net/static/images/icon-svg/common/share/facebook.svg" alt="FACEBOOK">
            <img src="https://d2q7nqismduvva.cloudfront.net/static/images/icon-svg/common/share/twitter.svg" alt="TWITTER">
        </div>
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact support@ninja.org.
    """.format(match.name, closing_time, report_time, dispute_time, link, link)

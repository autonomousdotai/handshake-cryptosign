#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
import app.constants as CONST


from flask import g
from app.models import Match
from datetime import datetime
from app.helpers.utils import render_unsubscribe_url, second_to_strftime, render_generate_link
from app.constants import Handshake as HandshakeStatus

def render_email_subscribe_content(passphase, match_id, user_id):
    return """
        Hey Ninja!<br/><br/>
        You’ve successfully made a prediction: <br/><br/>
        {}
        Great work! We’ll email you the result as soon as it’s been reported.<br/><br/>
        Enjoy daydreaming about all of the things you’ll (hopefully) do with your winnings.<br/><br/>
        Stay cool.<br/><br/>
        {}
    """.format(render_match_content(match_id), render_signature_content())


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


def render_verification_success_mail_content(match_id, uid):
    return """
        Hey Ninja,<br/><br/>
        Good news; your event (below) has been verified and will now appear on the exchange! <br/><br/>
        {}
        <b>Invite your friends to bet on this market by sharing the direct link below:</b><br/>
        {}<br/><br/>
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact <a href="mailto:support@ninja.org">support@ninja.org</a>.<br/><br/>
        Good luck!<br/>
        {}
    """.format(render_match_content(match_id), "{}prediction/{}".format(g.BASE_URL, render_generate_link(match_id, uid)), render_signature_content())


def render_verification_failed_mail_content(match_id):
    return """
        Hey Ninja,<br/><br/>
        There was an issue with the below event and we weren’t able to list it on the exchange. <br/>
        {}
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact <a href="mailto:support@ninja.org">support@ninja.org</a>.<br/><br/>
        Good luck!<br/>
        {}
    """.format(render_match_content(match_id), render_signature_content())


def render_create_new_market_mail_content(match_id):
    return """
        Hey Ninja,<br/><br/>
        Congratulations; your event was created successfully!  <br/>
        We’ll send you an email shortly to let you know if your market was approved, before adding it to the exchange. <br/>
        <b>Note:</b> Due to the approval process, it can take up to one hour for new events to appear on the exchange. <br/>
        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;In the meantime, please review the event details below: <br/>
        {}
        If you have any questions, please get in touch with us on <a href="http://t.me/ninja_org">Telegram</a> or contact <a href="mailto:support@ninja.org">support@ninja.org</a>.<br/><br/>
        Good luck!<br/>
        {}
    """.format(render_match_content(match_id), render_signature_content())


def render_signature_content():
    return """
        Ninja.org<br/>
        Join us on Telegram: <a href="http://t.me/ninja_org">http://t.me/ninja_org</a><br/>
        <div>
            <span style="">Find us on </span>
            <a href="https://www.facebook.com/ninjadotorg"><img height="30" width="30" style="vertical-align:middle" src="https://storage.googleapis.com/cryptosign/images/email_flows/facbook.png" alt="Facebook"></a>
            <a href="https://twitter.com/ninjadotorg"><img height="30" width="30" style="vertical-align:middle" src="https://storage.googleapis.com/cryptosign/images/email_flows/twitter.png" alt="Twitter"></a>
        </div>
    """


def render_match_content(match_id):
    match = Match.find_match_by_id(match_id)
    closing_time = second_to_strftime(match.date) 
    report_time = second_to_strftime(match.reportTime)
    dispute_time = second_to_strftime(match.disputeTime)
    return """
        <div>
            <blockquote style="margin:0 0 15px 15px;border:none;padding:0px">
                <div>
                    <b>Event name:</b> {}<br/>
                    <b>Your event ends:</b> {} (UTC)<br/>
                    <b>Report results before:</b> {} (UTC)<br/>
                    <b>Event closes:</b> {} (UTC) (if there’s no dispute)<br/>
                </div>
            </blockquote>
        </div>
    """.format(match.name, closing_time, report_time, dispute_time)
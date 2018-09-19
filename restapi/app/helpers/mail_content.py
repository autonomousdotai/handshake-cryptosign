#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import json
import time
import app.constants as CONST

from datetime import datetime
from app.helpers.utils import render_unsubscribe_url
from app.constants import Handshake as HandshakeStatus

def render_email_content(email, address, unsubscribe_url):
	mail_content = """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja Subscribe Email</title>
            <style>
            /* -------------------------------------
                GLOBAL RESETS
            ------------------------------------- */
            img {
                border: none;
                -ms-interpolation-mode: bicubic;
                max-width: 100%; }
            body {
                background-color: #f6f6f6;
                font-family: sans-serif;
                -webkit-font-smoothing: antialiased;
                font-size: 14px;
                line-height: 1.4;
                margin: 0;
                padding: 0;
                -ms-text-size-adjust: 100%;
                -webkit-text-size-adjust: 100%; }
            table {
                border-collapse: separate;
                mso-table-lspace: 0pt;
                mso-table-rspace: 0pt;
                width: 100%; }
                table td {
                font-family: sans-serif;
                font-size: 14px;
                vertical-align: top; }
            /* -------------------------------------
                BODY & CONTAINER
            ------------------------------------- */
            .body {
                background-color: #f6f6f6;
                width: 100%; }
            /* Set a max-width, and make it display as block so it will automatically stretch to that width, but will also shrink down on a phone or something */
            .container {
                display: block;
                Margin: 0 auto !important;
                /* makes it centered */
                max-width: 580px;
                padding: 10px;
                width: 580px; }
            /* This should also be a block element, so that it will fill 100% of the .container */
            .content {
                box-sizing: border-box;
                display: block;
                Margin: 0 auto;
                max-width: 580px;
                padding: 10px; }
            /* -------------------------------------
                HEADER, FOOTER, MAIN
            ------------------------------------- */
            .main {
                background: #ffffff;
                border-radius: 3px;
                width: 100%; }
            .wrapper {
                box-sizing: border-box;
                padding: 20px; }
            .content-block {
                padding-bottom: 10px;
                padding-top: 10px;
            }
            .footer {
                clear: both;
                Margin-top: 10px;
                text-align: center;
                width: 100%; }
                .footer td,
                .footer p,
                .footer span,
                .footer a {
                color: #999999;
                font-size: 12px;
                text-align: center; }
            /* -------------------------------------
                TYPOGRAPHY
            ------------------------------------- */
            h1,
            h2,
            h3,
            h4 {
                color: #000000;
                font-family: sans-serif;
                font-weight: 400;
                line-height: 1.4;
                margin: 0;
                Margin-bottom: 30px; }
            h1 {
                font-size: 35px;
                font-weight: 300;
                text-align: center;
                text-transform: capitalize; }
            p,
            ul,
            ol {
                font-family: sans-serif;
                font-size: 14px;
                font-weight: normal;
                margin: 0;
                Margin-bottom: 15px; }
                p li,
                ul li,
                ol li {
                list-style-position: inside;
                margin-left: 5px; }
            a {
                color: #3498db;
                text-decoration: underline; }
            /* -------------------------------------
                BUTTONS
            ------------------------------------- */
            .btn {
                box-sizing: border-box;
                width: 100%; }
                .btn > tbody > tr > td {
                padding-bottom: 15px; }
                .btn table {
                width: auto; }
                .btn table td {
                background-color: #ffffff;
                border-radius: 5px;
                text-align: center; }
                .btn a {
                background-color: #ffffff;
                border: solid 1px #3498db;
                border-radius: 5px;
                box-sizing: border-box;
                color: #3498db;
                cursor: pointer;
                display: inline-block;
                font-size: 14px;
                font-weight: bold;
                margin: 0;
                padding: 12px 25px;
                text-decoration: none;
                text-transform: capitalize; }
            .btn-primary table td {
                background-color: #3498db; }
            .btn-primary a {
                background-color: #3498db;
                border-color: #3498db;
                color: #ffffff; }
            /* -------------------------------------
                OTHER STYLES THAT MIGHT BE USEFUL
            ------------------------------------- */
            .last {
                margin-bottom: 0; }
            .first {
                margin-top: 0; }
            .align-center {
                text-align: center; }
            .align-right {
                text-align: right; }
            .align-left {
                text-align: left; }
            .clear {
                clear: both; }
            .mt0 {
                margin-top: 0; }
            .mb0 {
                margin-bottom: 0; }
            .preheader {
                color: transparent;
                display: none;
                height: 0;
                max-height: 0;
                max-width: 0;
                opacity: 0;
                overflow: hidden;
                mso-hide: all;
                visibility: hidden;
                width: 0; }
            .powered-by a {
                text-decoration: none; }
            hr {
                border: 0;
                border-bottom: 1px solid #f6f6f6;
                Margin: 20px 0; }
            /* -------------------------------------
                RESPONSIVE AND MOBILE FRIENDLY STYLES
            ------------------------------------- */
            @media only screen and (max-width: 620px) {
                table[class=body] h1 {
                font-size: 28px !important;
                margin-bottom: 10px !important; }
                table[class=body] p,
                table[class=body] ul,
                table[class=body] ol,
                table[class=body] td,
                table[class=body] span,
                table[class=body] a {
                font-size: 16px !important; }
                table[class=body] .wrapper,
                table[class=body] .article {
                padding: 10px !important; }
                table[class=body] .content {
                padding: 0 !important; }
                table[class=body] .container {
                padding: 0 !important;
                width: 100% !important; }
                table[class=body] .main {
                border-left-width: 0 !important;
                border-radius: 0 !important;
                border-right-width: 0 !important; }
                table[class=body] .btn table {
                width: 100% !important; }
                table[class=body] .btn a {
                width: 100% !important; }
                table[class=body] .img-responsive {
                height: auto !important;
                max-width: 100% !important;
                width: auto !important; }}
            /* -------------------------------------
                PRESERVE THESE STYLES IN THE HEAD
            ------------------------------------- */
            @media all {
                .ExternalClass {
                width: 100%; }
                .ExternalClass,
                .ExternalClass p,
                .ExternalClass span,
                .ExternalClass font,
                .ExternalClass td,
                .ExternalClass div {
                line-height: 100%; }
                .apple-link a {
                color: inherit !important;
                font-family: inherit !important;
                font-size: inherit !important;
                font-weight: inherit !important;
                line-height: inherit !important;
                text-decoration: none !important; }
                .btn-primary table td:hover {
                background-color: #34495e !important; }
                .btn-primary a:hover {
                background-color: #34495e !important;
                border-color: #34495e !important; } }
            </style>
        </head>
        <body class="">
            <table border="0" cellpadding="0" cellspacing="0" class="body">
            <tr>
                <td>&nbsp;</td>
                <td class="container">
                <div class="content">

                    <!-- START CENTERED WHITE CONTAINER -->
                    <span class="preheader">This is preheader text. Some clients will show this text as a preview.</span>
                    <table class="main">

                    <!-- START MAIN CONTENT AREA -->
                    <tr>
                        <td class="wrapper">
                        <table border="0" cellpadding="0" cellspacing="0">
                            <tr>
                            <td>
                                <p>Hi there,</p>
                                <p>Sometimes you just want to send a simple HTML email with a simple design and clear call to action. This is it.</p>
                                <table border="0" cellpadding="0" cellspacing="0" class="btn btn-primary">
                                <tbody>
                                    <tr>
                                    <td align="left">
                                        <table border="0" cellpadding="0" cellspacing="0">
                                        <tbody>
                                            <tr>
                                            <td> <a href="http://ninja.org" target="_blank">Call To Action</a> </td>
                                            </tr>
                                        </tbody>
                                        </table>
                                    </td>
                                    </tr>
                                </tbody>
                                </table>
                                <p>This is a really simple email template. Its sole purpose is to get the recipient to click the button with no distractions.</p>
                                <p>Good luck! Hope it works.</p>
                            </td>
                            </tr>
                        </table>
                        </td>
                    </tr>

                    <!-- END MAIN CONTENT AREA -->
                    </table>

                    <!-- START FOOTER -->
                    <div class="footer">
                    <table border="0" cellpadding="0" cellspacing="0">
                        <tr>
                        <td class="content-block">
                            <span class="apple-link">Company Ninja</span>
                            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
                        </td>
                        </tr>
                        <tr>
                        <td class="content-block powered-by">
                            Powered by <a href="http://ninja.org">HTMLemail</a>.
                            <img src="https://storage.googleapis.com/cryptosign/images/ninja.svg" alt="Ninja">
                        </td>
                        </tr>
                    </table>
                    </div>
                    <!-- END FOOTER -->

                <!-- END CENTERED WHITE CONTAINER -->
                </div>
                </td>
                <td>&nbsp;</td>
            </tr>
            </table>
        </body>
        </html>
    """.format(unsubscribe_url)
	return mail_content


def render_email_subscribe_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja Subscribe Email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>You’ve successfully made a prediction. Go you!    </p>
            <p>We’ll email you the result, the minute it comes in. </p>
            <p>Enjoy daydreaming about all of the things you’ll (hopefully) do with your winnings.</p>
            <p>Stay cool. </p>
            <p>Ninja</p>

            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_lose_free_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>Not so lucky this time :( </p>
            <p>But you know what we say... </p>
            <p>If at first you don’t succeed, try again for free.</p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_win_free_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>YOU WON! </p>
            <p>Wanna win more? </p>
            <p>Of course you do, who doesn’t!</p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_draw_free_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>So... it’s a DRAW. </p>
            <p>Wanna another shot at glory? </p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_not_match_free_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>Unfortunately, this time you weren't matched. </p>
            <p>No worries, let’s have another go. </p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_lose_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>Sorry, you lost :( </p>
            <p>You know what they say... </p>
            <p>"If at first you don’t succeed, try again for free."</p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))

def render_email_win_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>YOU WON! </p>
            <p>Congrats, you’ve successfully predicted the future.</p>
            <p>Wanna see if you can do it again? </p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_draw_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>So... it’s a DRAW. </p>
            <p>Not to worry, there’s always next time. </p>
            <p>We believe in you! </p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_not_match_real_bet_content(app, user_id):
    passphase = app.config["PASSPHASE"]
    return """
    <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Ninja results email</title>
        </head>
        <body class="">
            <p>Hey Ninja!</p>
            <p>Unfortunately, this time you weren't matched. </p>
            <p>Luckily, you can always try again. </p>
            <p>Let’s do it!</p>
            <p><a href="http://ninja.org/prediction">PLAY NOW</a></p>
            <br> Don't like these emails? <a href="{}">Unsubscribe</a>.
            <br>Powered by <a href="http://ninja.org">Ninja</a>.
            <br><a href="http://ninja.org"> <img src="" alt="Ninja"> </a>
        </html>
    """.format(render_unsubscribe_url(user_id, passphase))


def render_email_notify_result_content(app, user_id, address, outcome_name, match_name, outcome_result, bet_side, status, is_free_bet, free_bet_available):
    content = ""

    if is_free_bet:
        # if status == HandshakeStatus['STATUS_SHAKER_SHAKED']:
        if status == HandshakeStatus['STATUS_MAKER_SHOULD_UNINIT']:
            content = render_email_not_match_free_bet_content(app, user_id)
        else:
            if outcome_result == CONST.RESULT_TYPE["DRAW"]:
                content = render_email_draw_free_bet_content(app, user_id)
            else:
                if outcome_result == bet_side:
                    content = render_email_win_free_bet_content(app, user_id)
                else:
                    content = render_email_lose_free_bet_content(app, user_id)
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
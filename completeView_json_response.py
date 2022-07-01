https://mobiletrade.sit.etrade.com/phx/etm/services/v1/account/completeView
  
 payload:
  
  {
  "completeView": "",
  "displayPositions": true,
  "displayPositionsForMultiAccount": false
}


  
Response:   
{
    "mobile_response": {
        "views": [
            {
                "type": "net_assets_summary",
                "data": {
                    "account_uuids": [
                        "NjM0NzcwNjJ8QnJva2VyYWdlfEFEUHw2NjY2NjZ8LXwt"
                    ],
                    "account_summary_label": "Net Assets",
                    "account_summary_streamable_value": {
                        "initial": "$10,125,057.36",
                        "stream_id": "NET_ASSETS",
                        "local_field_name": null,
                        "movement_type": "gain"
                    }
                },
                "cta": null,
                "action": null
            },
            {
                "type": "net_gain_summary",
                "data": {
                    "account_uuids": [
                    ],
                    "account_summary_label": "Day's Gain",
                    "account_summary_streamable_value": {
                        "initial": "$0.00",
                        "stream_id": "DAYS_GAIN",
                        "local_field_name": null,
                        "movement_type": "neutral"
                    }
                },
                "cta": null,
                "action": null
            },
            {
                "type": "account_summary",
                "data": {
                    "account_uuid": "NjM0NzcwNjJ8QnJva2VyYWdlfEFEUHw2NjY2NjZ8LXwt",
                    "account_name": "Individual Brokerage -7062",
                    "account_detail_label": "Net Account Value",
                    "account_detail_value": "$10,125,057.36",
                    "account_additional_labels": [
                        {
                            "account_additional_label_title": "Day's Gain",
                            "account_additional_label_streamable_value": {
                                "initial": "-- (--)",
                                "stream_id": "DAYS_GAIN",
                                "local_field_name": null
                            },
                            "account_additional_label_value_detail": null
                        },
                        {
                            "account_additional_label_title": "Total Gain",
                            "account_additional_label_streamable_value": {
                                "initial": "-- (--)",
                                "stream_id": "TOTAL_GAIN",
                                "local_field_name": null
                            },
                            "account_additional_label_value_detail": null
                        },
                        {
                            "account_additional_label_title": "Cash",
                            "account_additional_label_streamable_value": {
                                "initial": "$10,100,003.85",
                                "stream_id": null,
                                "local_field_name": null,
                                "movement_type": "neutral"
                            }
                        }
                    ]
                },
                "cta": [
                    {
                        "cta_label": "View Portfolio",
                        "cta_action": {
                            "app_url": "etrade://account/63477062/portfolio",
                            "web_url": "",
                            "webview_url": ""
                        }
                    }
                ],
                "action": {
                    "app_url": "etrade://account/63477062/overview",
                    "web_url": "",
                    "webview_url": ""
                }
            }
        ],
        "references": [
            {
                "type": "accounts",
                "data": [
                    {
                        "accountUuid": "NjM0NzcwNjJ8QnJva2VyYWdlfEFEUHw2NjY2NjZ8LXwt",
                        "accountId": "63477062",
                        "formattedAcctNumber": "6347-7062",
                        "accountMode": "MARGIN",
                        "acctDesc": "Individual Brokerage",
                        "accountShortName": "Individual Brokerage -7062",
                        "accountLongName": "Individual Brokerage 6347-7062",
                        "acctType": "Brokerage",
                        "instType": "ADP",
                        "isLiabilityAccount": false,
                        "isIRA": false,
                        "encAccountId": null,
                        "accountValue": "$10,125,057.36",
                        "cashAvailableForWithdrawal": "$10,099,326.30",
                        "daysGain": "--",
                        "daysGainPercent": "--",
                        "funded": true,
                        "ledgerAccountValue": "$10,100,003.85",
                        "maFlag": false,
                        "marginAvailableForWithdrawal": "$0.75",
                        "purchasingPower": "$20,198,654.10",
                        "restrictionLevel": "0",
                        "streamingRestrictions": {
                            "accountStreaming": true
                        },
                        "totalAvailableForWithdrawal": "$10,099,327.05",
                        "totalGain": "--",
                        "totalGainPercent": "--",
                        "promptsForFunding": null
                    }
                ]
            },
            {
                "type": "positions",
                "data": [
                ]
            },
            {
                "type": "instruments",
                "data": [
                ]
            }
        ],
        "meta": null
    }
}

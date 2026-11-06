# Pile hand-check sample

10 random documents per subject from the **test** halves, first 1,500 characters of the cleaned text. Seeded from the data seed, so a rebuild shows the same documents.

**What to check:** the text reads like the subject its label claims; cleaning has not mangled it (code keeps its indentation, prose keeps its paragraphs); nothing looks like boilerplate repeated across documents; `ngram_overlap` is low except where the subject is self-overlapping by nature (`Github`, `FreeLaw`).

## Pile-CC

41 documents in the test half; 10 shown.

### `pile_cc-val-105`

- tokens: 124
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 105

```text
Mutt fucke himself 1 year ago today. thanks mutt, I would have never found SFSN without your help & never found this place. I want to thank "bethsucks" for SFSN & Dawg, Monk, Elias & Spazz; for what we have today.
you fuckers rock our world.

I'd pay big money to see one interviewer ask Howard some embarassing questions like that. Things like "What exactly IS that thing on your head?" or "Do you ever feel guilty about getting rich off your fans and then pissing on them?".
```

### `pile_cc-val-109`

- tokens: 94
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 109

```text
SJP and MB: Lights, Camera, Relationship

7/31/2008 1:05 PM PDT

SJP and MB: Lights, Camera, Relationship

What infidelity rumors?Sarah Jessica Parker and Matthew Broderick had dinner in NYC last night despite rampant Internet rumors about Matthew cheating. If they go out in public together, they must be happy!

Looks like neither has broken things off yet, via Post-it or otherwise.
```

### `pile_cc-val-115`

- tokens: 132
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 115

```text
Multiple Image Layout

Below is a working example of this template. You'll find simple instructions of how to use it beneath it. This particular template provides interaction with its viewer. All four images have links attached to them, they just need to be specified/customized by right clicking on the image and clicking "Insert/edit link". This also applies to the links below the images.

You can customize:

Images

Text

'href' links

You cannot customize:

Image size

Layout

Spacing between images

Note: for images to display properly in this template, use these sizes:
```

### `pile_cc-val-116`

- tokens: 326
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 116

```text
We all know that RiRi and Breezy had one of the most colorful history among celebrity couples. The pair had a roller coaster romance and have broken up and rekindled their relationship a couple of times before permanently calling it quits in 2014. Now some fans are panicking that Rihanna maybe missing her ex-boyfriend and could rekindle their old flame.

The Bajan pop beauty posted a pic of herself a few weeks back and captioned it, “When you hang up on em, then call right back. #firstofallimcrazy #secondofalliwasntdone.” Chris Brown has a song on his new album Heartbreak On a Full Moon titled “Other Ni**as” where he sing some similar lines.

“Oh girl, why you gotta be like that? (Girl, like that) / Why gotta hang up on me then you call right back? (Back) / How you compare me to them ni**as that you gave your heart to? (Heart to),” Chris Brown sings. Rihanna made her Instagram post a few days before Brown drop the album and some fans are now saying that he might have given her a copy of the project before it was released, which means that they are secretly communicating with each other. On the other hand, it could be just share coincidence that RiRi made a quote identical to Breezy’s lyrics just a few days before he drop an album, just how likely is that. Listen to the full song “Other Ni**as” below.
```

### `pile_cc-val-147`

- tokens: 699
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 147

```text
O'Brien made these claims in the TranceFormation of America (1995) and Access Denied: For Reasons of National Security (2004) which she co-authored with Mark Phillips.[6] O'Brien is one of many people publicly claiming to have survived government-sponsored mind control programs.

O'Brien claims to have been abused since she was a toddler. Forced to partake in satanic sadomasochistic child pornography movies produced for Gerald Ford, she was eventually sold to the CIA, which was looking for traumatized children for their mind-control program ... U.S. Presidents Ford, [and many other world leaders] all sexually brutalized her. She recounts in graphic detail how the elder George Bush raped her thirteen year old daughter and how she was forced to have oral sex with Illuminati witch Hillary Clinton ... While being sodomized, whipped, bound and raped, O'Brien overheard the globalist elite planning a military coup in the United States and conspiring to usher in the satanic New World Order. (Gardell, 97-98)

On websites, O'Brien claims she was rescued in 1988, which suggests that her daughter Kelly was no more than eight years old when last abused. Phillips stated in a Granada Forum lecture in 1996 that Kelly was in fact institutionalized when she was eight and has been raised in a mental institution.

Although he has since distanced himself from studies in mind control, licensed psychologist Corydon Hammond seems to confirm as credible accounts similar to O'Brien's in a speech he de
…[truncated]
```

### `pile_cc-val-19`

- tokens: 150
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 19

```text
Wednesday, May 24, 2017

Facebook redesigns Trending topics to make news easier to find

Facebook is introducing a couple of changes today that make it easier to spot trending topics and the coverage around them. First up, there’s a bit of a visual redesign. Previously, clicking on a trending topic would highlight a story from one publication, and you’d have to scroll down past a live video section to view related stories. Facebook is replacing that system with a simple carousel, which does a better job of showing you different coverage options. To be clear, the change doesn’t affect how stories are sourced, according to Facebook. It’s still the same algorithm picking out some of the most…
```

### `pile_cc-val-223`

- tokens: 755
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 223

```text
HealthChoice Pharmacy Benefit

The member is responsible for the appropriate copay or the actual cost of the prescription; whichever is less, when a Network Pharmacy is utilized. Only the costs of generic medications are covered unless there is no generic equivalent available. If a generic medication is available, but the member requests the brand name equivalent, the member will be responsible for the copay amount plus the cost difference between the brand name medication and the generic equivalent. Some medications require prior authorization or may have quantity limits. Please contact the Pharmacy Benefits Manager, Medco at 1-800-903-8113, for information regarding quantity limits and to obtain prior authorization.

A list of preferred medications is included in the HealthChoice Select Medication List. A copy of this medication list is available on the provider website or you may request a list through the Provider Relations Division.

HealthChoice Select Medication List (HSML)

The HealthChoice Select Medication List is based on optimum therapy strategies and the evaluation of clinically equivalent medications. These evaluations are performed by the pharmaceutical consultant for OSEEGIB and the clinical staff of the pharmacy benefits manager. A list of preferred and non-preferred medications has been established and members obtain preferred medications (medications included on the Select Medication List) by paying the cost of the medication up to a $25 maximum if the cost
…[truncated]
```

### `pile_cc-val-236`

- tokens: 1,100
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 236

```text
All-terrain vehicle enthusiasts are pushing to get more access to local roads, including roads in unincorporated Spokane County.

But Spokane County commissioners last week said they are initially reluctant to open county roads to ATVs, despite a new state law allowing it.

Lawmakers last spring approved ATVs on roads with speed limits of 35 mph or lower but gave control over the decision to local governments.

Rep. Matt Shea, R-Spokane Valley, was the prime sponsor of the bill.

The problem has been Washington’s “overly restrictive laws concerning the use of off-road vehicles and all-terrain vehicles,” Shea said in a news release when the bill passed in June.

The law was described as a compromise among ATV enthusiasts, conservationists and government.

The law sets up a licensing system for ATVs, intended to control illegal off-road use of the vehicles and prevent ATV thefts.

Licensed ATVs would need safety and other equipment, such as spark arrestors, to be allowed on regular roads.

Shea and ATV users said opening local roads to the vehicles would create tourist opportunities in rural areas where economies have been depressed over the years.

It would also create new, legal riding opportunities closer to home, said Bob Cahill, president of the Eastern Washington ATV Association.

“I think there are lots of roads that could be opened to ATVs in this county,” he said.

Cahill said he travels to other states to ride and has discovered the draw of ATVs provides economic stim
…[truncated]
```

### `pile_cc-val-52`

- tokens: 109
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 52

```text
Grafana Labs Blog

Covered in this article:
Lucene Query Format Templated Queries Sawtooth-Like Graphs Incomplete data at the beginning and the end of a graph Sum function broken About one year after I created an issue at Grafana’s GitHub page, we finally have support for using Elasticsearch as a time series database! At that time, I was trying to lower the burden of adopting the open source Java performance monitoring tool stagemonitor which I’m the project lead of.
```

### `pile_cc-val-54`

- tokens: 51
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 54

```text
BookGoodies host Deborah Carney is joined by indie author PJ Sharon to discuss why she chose to publish independently and share her tips on becoming a successfully published author. Some of the resources PJ shared are below, there are many more great tips in the podcast.
```

## Github

18 documents in the test half; 10 shown.

### `github-val-1`

- tokens: 72
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 1

```text
### Solution for "Download of Code Without Integrity Check" challenge

This challenge showcases a situation common to software deployments where an update server is being used but integrity checks are no in place in order to validate the software has not been tampered with.

Only thing required to do in order to pass is changing the update server to `evil.bad`.
```

### `github-val-128`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 8.9128%
- source: `val.jsonl.zst` line 128

```text
#!/usr/bin/python
#
# Copyright 2018-2020 Polyaxon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# coding: utf-8

"""
    Polyaxon SDKs and REST API specification.

    Polyaxon SDKs and REST API specification. # noqa: E501

    The version of the OpenAPI document: 1.1.9-rc4
    Contact: contact@polyaxon.com
    Generated by: https://openapi-generator.tech
"""

import pprint
import re # noqa: F401

import six

from polyaxon_sdk.configuration import Configuration

class V1Queue(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        "uuid": "str",
        "agent": "str",
        "name": "
…[truncated]
```

### `github-val-175`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 4.3830%
- source: `val.jsonl.zst` line 175

```text
/*
 * Driver for audio on multifunction CS5535/6 companion device
 * Copyright (C) Jaya Kumar
 *
 * Based on Jaroslav Kysela and Takashi Iwai's examples.
 * This work was sponsored by CIS(M) Sdn Bhd.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 */

#include <linux/delay.h>
#include <linux/interrupt.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/slab.h>
#include <linux/module.h>
#include <linux/io.h>
#include <sound/core.h>
#include <sound/control.h>
#include <sound/pcm.h>
#include <sound/rawmidi.h>
#include <sound/ac97_codec.h>
#include <sound/initval.h>
#include <sound/asoundef.h>
#include "cs5535audio.h"

#define DRIVER_NAME "cs5535audio"

static char *ac97_quirk;
module_param(ac97_quirk, charp, 0444);
MODULE_PARM_DESC(ac97_quirk, "AC'97 board specific workarounds.");

static const struct ac97_qu
…[truncated]
```

### `github-val-303`

- tokens: 1,948
- 13-gram overlap with training text: 7.0764%
- source: `val.jsonl.zst` line 303

```text
/*************************************************************
 *
 * MathJax/jax/output/HTML-CSS/fonts/STIX/General/Bold/BBBold.js
 *
 * Copyright (c) 2009-2018 The MathJax Consortium
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */

MathJax.Hub.Insert(
  MathJax.OutputJax['HTML-CSS'].FONTDATA.FONTS['STIXGeneral-bold'],
  {
    0x1D538: [676,0,787,50,737], // MATHEMATICAL DOUBLE-STRUCK CAPITAL A
    0x1D539: [676,0,729,75,669], // MATHEMATICAL DOUBLE-STRUCK CAPITAL B
    0x1D53B: [676,0,748,75,703], // MATHEMATICAL DOUBLE-STRUCK CAPITAL D
    0x1D53C: [676,0,650,75,595], // MATHEMATICAL DOUBLE-STRUCK CAPITAL E
    0x1D53D: [676,0,474,75,595], // MATHEMATICAL DOUBLE-STRUCK CAPITAL F
    0x1D53E: [691,19,751,45,686], // MATHEMATICAL DOUBLE-STRUCK CAPITAL G
    0x1D540: [676,0,380,80,300], // MATHEMATICAL DOUBLE-STRUCK CAPITAL I
    0x1D541: [676,19,618,50,548], // MATHEMATICAL DOUBLE-STRUCK CAPITAL J
    0x1D542: [676,0,792,75,767], // MATHEMATICAL DOUBLE-STRUCK CAPITAL K
   
…[truncated]
```

### `github-val-312`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 8.1293%
- source: `val.jsonl.zst` line 312

```text
import { FocusZoneDirection } from '@fluentui/accessibility';
import { FocusTrapZone, FocusZone, FocusTrapZoneProps } from '@fluentui/react-bindings';
import * as React from 'react';
import * as ReactTestUtils from 'react-dom/test-utils';
import { keyboardKey } from '@fluentui/keyboard-key';

// rAF does not exist in node - let's mock it
window.requestAnimationFrame = (callback: FrameRequestCallback) => {
  const r = window.setTimeout(callback, 0);
  jest.runAllTimers();
  return r;
};

jest.useFakeTimers();

class FocusTrapZoneTestComponent extends React.Component<{}, { isShowingFirst: boolean; isShowingSecond: boolean }> {
  constructor(props: {}) {
    super(props);
    this.state = { isShowingFirst: true, isShowingSecond: false };
  }

  render() {
    return (
      <div>
        <FocusTrapZone forceFocusInsideTrapOnOutsideFocus isClickableOutsideFocusTrap={false}>
          <button className={'a'} onClick={this._toggleFirst}>
            a
          </button>
          <button className={'b'} onClick={this._toggleSecond}>
            b
          </button>
        </FocusTrapZone>

        {this.state.isShowingFirst && (
          <FocusTrapZone forceFocusInsideTrapOnOutsideFocus={false} isClickableOutsideFocusTrap={false}>
            <FocusZone data-is-visible={true}>First</FocusZone>
          </FocusTrapZone>
        )}
        {this.state.isShowingSecond && (
          <FocusTrapZone forceFocusInsideTrapOnOutsideFocus={false} isClickableOutsideFocusTrap={true}>
    
…[truncated]
```

### `github-val-32`

- tokens: 292
- 13-gram overlap with training text: 1.7857%
- source: `val.jsonl.zst` line 32

```text
THE_URL:file://localhost/Users/hubery/Public/ucar/Document/Functions/Contributed/zonalAve.shtml
THE_TITLE:zonalAve
   NCL Home > Documentation > Functions > General applied math

zonalAve

   Computes a zonal average of the input array.

Prototype

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"

        function zonalAve (
                x : numeric
        )

        return_val : typeof(x)

Arguments

   x

   An array of any size and type.

Return value

   The results are returned in an array of the same type and one dimension smaller than x. Metadata are preserved.

Description

   This function computes a zonal average of the input array x. If the input array has a "long_name" or "short_name"
   attribute, it will be updated.

   Â©2015 UCAR | Privacy Policy | Terms of Use | Contact the Webmaster | Sponsored by NSF
```

### `github-val-63`

- tokens: 801
- 13-gram overlap with training text: 10.0127%
- source: `val.jsonl.zst` line 63

```text
{
  "_from": "isstream@~0.1.2",
  "_id": "isstream@0.1.2",
  "_inBundle": false,
  "_integrity": "sha1-R+Y/evVa+m+S4VAOaQ64uFKcCZo=",
  "_location": "/isstream",
  "_phantomChildren": {},
  "_requested": {
    "type": "range",
    "registry": true,
    "raw": "isstream@~0.1.2",
    "name": "isstream",
    "escapedName": "isstream",
    "rawSpec": "~0.1.2",
    "saveSpec": null,
    "fetchSpec": "~0.1.2"
  },
  "_requiredBy": [
    "/request"
  ],
  "_resolved": "https://registry.npmjs.org/isstream/-/isstream-0.1.2.tgz",
  "_shasum": "47e63f7af55afa6f92e1500e690eb8b8529c099a",
  "_spec": "isstream@~0.1.2",
  "_where": "/Users/rhwood/Developer/JMRI/JMRI/rhwood/JMRI/web/app/node_modules/request",
  "author": {
    "name": "Rod Vagg",
    "email": "rod@vagg.org"
  },
  "bugs": {
    "url": "https://github.com/rvagg/isstream/issues"
  },
  "bundleDependencies": false,
  "deprecated": false,
  "description": "Determine if an object is a Stream",
  "devDependencies": {
    "core-util-is": "~1.0.0",
    "inherits": "~2.0.1",
    "isarray": "0.0.1",
    "string_decoder": "~0.10.x",
    "tape": "~2.12.3"
  },
  "homepage": "https://github.com/rvagg/isstream",
  "keywords": [
    "stream",
    "type",
    "streams",
    "readable-stream",
    "hippo"
  ],
  "license": "MIT",
  "main": "isstream.js",
  "name": "isstream",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/rvagg/isstream.git"
  },
  "scripts": {
    "test": "tar --xform 's/^package/readable-stream-1.0
…[truncated]
```

### `github-val-69`

- tokens: 1,155
- 13-gram overlap with training text: 0.9624%
- source: `val.jsonl.zst` line 69

```text
/* LibTomCrypt, modular cryptographic library -- Tom St Denis
 *
 * LibTomCrypt is a library that provides various cryptographic
 * algorithms in a highly modular and flexible manner.
 *
 * The library is free for all purposes without any express
 * guarantee it works.
 *
 * Tom St Denis, tomstdenis@gmail.com, http://libtom.org
 */
#include "../../headers/tomcrypt.h"

/**
  @file der_decode_integer.c
  ASN.1 DER, decode an integer, Tom St Denis
*/

#ifdef LTC_DER

/**
  Read a mp_int integer
  @param in The DER encoded data
  @param inlen Size of DER encoded data
  @param num The first mp_int to decode
  @return CRYPT_OK if successful
*/
int der_decode_integer(const unsigned char *in, unsigned long inlen, void *num)
{
   unsigned long x, y, z;
   int err;

   LTC_ARGCHK(num != NULL);
   LTC_ARGCHK(in != NULL);

   /* min DER INTEGER is 0x02 01 00 == 0 */
   if (inlen < (1 + 1 + 1)) {
      return CRYPT_INVALID_PACKET;
   }

   /* ok expect 0x02 when we AND with 0001 1111 [1F] */
   x = 0;
   if ((in[x++] & 0x1F) != 0x02) {
      return CRYPT_INVALID_PACKET;
   }

   /* now decode the len stuff */
   z = in[x++];

   if ((z & 0x80) == 0x00) {
      /* short form */

      /* will it overflow? */
      if (x + z > inlen) {
         return CRYPT_INVALID_PACKET;
      }

      /* no so read it */
      if ((err = mp_read_unsigned_bin(num, (unsigned char *)in + x, z)) != CRYPT_OK) {
         return err;
      }
   } else {
      /* long form */
      z &= 0x7F;

      /* will numb
…[truncated]
```

### `github-val-91`

- tokens: 158
- 13-gram overlap with training text: 5.4795%
- source: `val.jsonl.zst` line 91

```text
/**
 * Created by martin on 19.02.2017.
 */
import * as path from 'path';

let pkg = null;
try {
    pkg = require(path.resolve(__dirname, '..', 'package.json'));
} catch (e) {
    try {
        pkg = require(path.resolve(__dirname, '..', '..', 'package.json'));
    } catch (e) {
        pkg = null;
    }
}

export const VERSION = (pkg ? pkg.version : 'unknown');
```

### `github-val-94`

- tokens: 1,247
- 13-gram overlap with training text: 0.2429%
- source: `val.jsonl.zst` line 94

```text
'use strict';

var Promise = require('sporks/scripts/promise'),
  sporks = require('sporks');

var Config = function (slouch) {
  this._slouch = slouch;
};

Config.prototype._couchDB2Request = function (node, path, opts, parseBody) {
  opts.uri = this._slouch._url + '/_node/' + node + '/_config/' + path;
  opts.parseBody = parseBody;
  return this._slouch._req(opts);
};

// Warning: as per https://github.com/klaemo/docker-couchdb/issues/42#issuecomment-169610897, this
// isn't really the best approach as a more complete solution would implement some rollback
// mechanism when a node fails after several attempts. (Retries are already attempted by the
// request).
Config.prototype._couchDB2Requests = function (path, opts, parseBody, maxNumNodes) {
  var self = this,
    promises = [],
    i = 0;

  return self._slouch.membership.get().then(function (members) {
    members.cluster_nodes.forEach(function (node) {
      if (typeof maxNumNodes === 'undefined' || i++ < maxNumNodes) {
        // Clone the opts as we need a separate copy per node
        var clonedOpts = sporks.clone(opts);
        promises.push(self._couchDB2Request(node, path, clonedOpts, parseBody));
      }
    });

    // Only return a single promise when there is a single promise so that the return value
    // is consistent for a single node.
    return promises.length > 1 ? Promise.all(promises) : promises[0];
  });
};

Config.prototype._couchDB1Request = function (path, opts, parseBody) {
  opts.uri = this._s
…[truncated]
```

## PubMed Central

7 documents in the test half; 7 shown.

### `pubmed_central-val-113`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.7835%
- source: `val.jsonl.zst` line 113

```text
INTRODUCTION {#s1}
============

Upper track urothelial carcinoma (UTUC) is less common than bladder urothelial carcinoma and accounts for 5--10% of all urothelial carcinoma.^[@b1]^ The incidence of ureteral urothelial carcinoma (UUC) is approximately half that of pyelocaliceal urothelial carcinoma.^[@b2]^ UUC has a worse prognosis than pyelocaliceal urothelial carcinoma.^[@b3],[@b4]^ Owing to different anatomical considerations and oncological outcomes in UTUC, these different malignant entities must be evaluated independently.^[@b5]^

The gold standard treatment for UTUC is radical nephroureterectomy with excision of the bladder cuff, regardless of the tumour location.^[@b6]^ Recently, conservative surgery such as endoscopic ablation or segmental ureteral resection, which allows preservation of the upper urinary renal unit, has also been applied.^[@b7]^ However, preoperative histological evaluation through biopsy of the upper urinary tract is difficult, because ureteroscopy is an invasive procedure and usually requires general anaesthesia. Furthermore, the accuracy of ureteroscopic biopsy in predicting tumour stage and grade is limited, and the limitations of endoscopic biopsy must be balanced against the possible advantage of avoiding radical surgery.^[@b8]^ Thus, accurate preoperative prediction of tumour grade could be helpful in selecting more appropriate therapeutic options.

CT urography (CTU) is an imaging modality with high diagnostic accuracy in the detection of UT
…[truncated]
```

### `pubmed_central-val-151`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 151

```text
Introduction {#S0001}
============

The rotator cuff tear is the most common tendinopathy in humans and over 200,000 cuff repairs are performed annually in the United States \[[1](#CIT0001),[2](#CIT0002)\]. The decreased morbidity associated with arthroscopic repairs has contributed to the popularity and broad indications for this surgical intervention \[[1](#CIT0001),[3](#CIT0003)\]. Tendon reattachment even if biomechanically strong at the time of repair often fails and approximately 50% of patients with full-thickness tears of the rotator cuff report symptoms at 6 months after surgery \[[1](#CIT0001),[4](#CIT0004),[5](#CIT0005)\].10.1080/21623945.2019.1609201-F0005Figure 5.Schematic representation of the changes in the number and cross-section area of fat clumps and of adipocyte number in the proximal, medial and distal SSP muscle after a complete SSP tendon detachment. IMF increased closer to the tendon tear compared to the proximal SSP muscle. Detached muscles had more clumps in the distal and medial sections and of larger size in the distal section. There were more adipocytes in the distal and medial detached SSP muscles compared to proximal and cross-sectional area was smaller in the distal SSP muscle. The fat clumps are represented by ovals and adipocytes by smaller filed black shapes. Results from the statistical analysis are indicated: 0.001 ≤ P \< 0.01 (\*), 0.0005 ≤ P \< 0.001 (\*\*), P \< 0.0005 (\*\*\*).

The unsatisfactory success of rotator cuff repair surgeri
…[truncated]
```

### `pubmed_central-val-225`

- tokens: 1,714
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 225

```text
Historically pulmonary emphysema was described in 1834 by Laennec on the basis of observations made on the cut surface of postmortem human lungs being the lesion attributed to the atrophy of lung tissue from pulmonary hyperinflation.^([@B1])^ Hence, emphysema was redefined as a "abnormal and permanent dilation of distal air spaces of terminal bronchiole".^([@B2])^ In addition, evidences of destruction of alveolar wall and fibrosis must not be ignored in this disease pathogenesis.^([@B3])^

These anatomopathological changes result in loss of respiratory surface and blood irrigation, decrease of elastic recognition and pulmonary hyperexpansion, and it could also affect part of acinus or its structure.^([@B4])^

Pulmonary emphysema is caused by enzymatic imbalance between proteases and anti-proteases that results in destruction of the alveolar wall due to proteolytic enzymes action, which affects the extracellular matrix (ECM)^([@B5])^ and its component integrity especially the elastic fibres.^([@B6])^

Experimental model of pulmonary emphysema is based on nebulization or instillation of proteolytic enzyme, such as panain *(Carica papaya)*,^([@B7])^ porcine pancreatic elastase,^([@B4])^ and human neutrophil elastase.^([@B8])^ This proteolytic process, associated with uniform destruction of ECM of pulmonary acinus, ends up in morphohistological and physiological changes in lungs that resemble those changes find in emphysema in humans.^([@B9],[@B10])^

Dilatation of distal air spa
…[truncated]
```

### `pubmed_central-val-307`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.3918%
- source: `val.jsonl.zst` line 307

```text
All relevant data can be found at the following URL: <https://doi.org/10.6084/m9.figshare.4640092.v1>.

Introduction {#sec001}
============

Length-weight relationships (LWR) are used for estimating the weight corresponding to a given length \[[@pone.0171811.ref001]\]. As most observations in fisheries surveys are typically obtained as the number of specimens and length of each sampled specimen, LWR are widely used to transform the survey data into estimates of the biomass which is important for modelling aquatic ecosystems. Therefore, estimation of the LWR is common practice and essential in fisheries science \[[@pone.0171811.ref002]\].

There are two parameters in the LWR model (*W* = *a*×*L*^*b*^), the coefficient *a* and the exponent *b*. Parameter *a* is the condition factor, describing body shape which can be classified as four groups: eel-like, elongated, fusiform and short and deep \[[@pone.0171811.ref002]\]. Parameter *b* is the allometric growth parameter, which indicates isometric growth in body proportions if *b*≥3 where fish have more girth as it grows longer; the species tends to be more streamlined if the exponent *b*\<3 \[[@pone.0171811.ref002]\].

Numerous studies found that factors, such as geographic, seasonal, inter-annual, and environmental conditions, can affect the estimates of *a* and *b* in the LWR model \[[@pone.0171811.ref002]--[@pone.0171811.ref005]\]. Instead of constructing several models reflecting various situations (different regions and years
…[truncated]
```

### `pubmed_central-val-35`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.0245%
- source: `val.jsonl.zst` line 35

```text
1. Introduction {#sec1-jcm-08-02039}
===============

Venous thromboembolism (VTE) is a common cause of morbidity and mortality in hospitalized and non-hospitalized patients \[[@B1-jcm-08-02039]\]. The American Society of Hematology and American College of Chest Physicians guidelines recommend low-molecular-weight heparin (LMWH) as a first-line pharmacological option for most patients at risk of VTE \[[@B2-jcm-08-02039],[@B3-jcm-08-02039]\]. Several prophylactic doses and types of LMWH are used worldwide, which is reflected by differences in national summaries of product characteristics (SPCs) and dosing regimens of randomized controlled trials (RCTs). There is no high-quality evidence or guidance on the optimal prophylactic LMWH dose. Preceding systematic reviews on thrombosis prophylaxis have not specifically assessed benefits and harms associated with different LMWH doses \[[@B4-jcm-08-02039],[@B5-jcm-08-02039],[@B6-jcm-08-02039],[@B7-jcm-08-02039],[@B8-jcm-08-02039],[@B9-jcm-08-02039],[@B10-jcm-08-02039]\]. In addition, there have been very few direct comparisons of prophylactic LMWH dose regimens, and therefore indirect evidence could provide a 'second best' estimate of benefits and harms.

There is no generally accepted definition of different prophylactic LMWH dose categories, which is why we previously categorized LMWH thrombosis prophylaxis regimens as either 'low-dose' or 'intermediate-dose', based on different registered doses in SPCs worldwide \[[@B11-jcm-08-02039
…[truncated]
```

### `pubmed_central-val-42`

- tokens: 3,441
- 13-gram overlap with training text: 1.0790%
- source: `val.jsonl.zst` line 42

```text
INTRODUCTION {#sec1-1}
============

Bonding of composite resin to dentin has always been a challenge for the clinicians. Although there is an improvement in handling and bonding characteristics of the newer dental materials,\[[@ref1][@ref2]\] the collagen structure and stability of the dentin bond strength are still a challenge. Studies have proved that collagen in the hybrid layer is affected by enzymatic degradation, leading to bond failure over time.\[[@ref3][@ref4]\]

Collagen fibrils in tissue are stabilized by lysyl oxidase-mediated covalent intermolecular cross-linking.\[[@ref5]\] The biomechanical properties of type I collagen can be improved by introducing more cross-links within and/or between the fibrils with the treatment of specific chemical agents.

Grape seed extract, which is a naturally occurring cross-linker, mainly composed of proanthocyanidins (PAs), could be a good candidate to fulfill such role. It is a natural plant metabolite and showed to possess low toxicity and ability to induce exogenous cross-links.\[[@ref6]\] PA-based compounds can improve dentin collagen physical properties.\[[@ref7][@ref8]\] Another such important agent is ascorbic acid. It is an essentially required component in the synthesis of hydroxyproline and hydroxylysine in collagen. Hydroxyproline serves to stabilize the collagen triple helix. Hydroxylysine is necessary for the formation of the intermolecular crosslinks in collagen. It is believed that ascorbate modulates collagen pro
…[truncated]
```

### `pubmed_central-val-43`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 43

```text
Introduction
============

Sickle cell disease (SCD) is a genetic disorder in which polymerization of deoxygenated sickle hemoglobin (HbS) leads to decreased deformability of the normally flexible erythrocytes. These rigid sickle-shaped red blood cells (RBC) can occlude the microvasculature leading to the sudden onset of painful vaso-occlusive episodes (VOC).^[@b1-1050083],[@b2-1050083]^ After HbS deoxygenates in the capillaries, it takes some time (seconds) for HbS polymerization and the subsequent flexible-to-rigid transformation. If the transit time of RBC through the microvasculature is longer than the polymerization time, sickled RBC will lodge in the microvasculature.^[@b3-1050083]^ Any trigger that decreases microvascular blood flow will prolong the transit time, promoting the entrapment of sickled RBC, resulting in vaso-occlusion. This physiology of SCD, described decades ago,^[@b4-1050083],[@b5-1050083]^ is fundamental to understanding the triggering of VOC. Patients report that stress, cold, and pain itself can trigger the onset of VOC^[@b6-1050083]^ but the frequency of VOC is highly variable. To date, the mechanism of how such events might trigger regional vaso-occlusion has not been fully elucidated.

Psychological stress is an exacerbating factor in many chronic illnesses, such as SCD,^[@b7-1050083]--[@b10-1050083]^ coronary artery disease and myocardial ischemia.^[@b11-1050083],[@b12-1050083]^ Stress is significantly associated with increased pain intensity, re
…[truncated]
```

## FreeLaw

10 documents in the test half; 10 shown.

### `freelaw-val-13`

- tokens: 3,667
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 13

```text
315 A.2d 483 (1974)
SEAWAY SHOPPING CENTER CORPORATION
v.
The GRAND UNION STORES, INC., OF VERMONT, and the Grand Union Company.
No. 3-73.
Supreme Court of Vermont, Chittenden.
February 5, 1974.
*484 James D. Foley, of Yandell, Page & Archer, Burlington, for plaintiff.
Wilson, Curtis, Bryan, Quinn & Jenkins, Burlington, for defendants.
Before SHANGRAW, C. J., and BARNEY, SMITH, KEYSER and DALEY, JJ.
SHANGRAW, Chief Justice.
This is an appeal from a judgment entered in a civil action tried by the Chittenden County Court on December 6, 1972. Jury trial was waived and following a hearing by the court plaintiff was awarded damages in the amount of $14,839.05 and its costs. A judgment for this amount followed, and the defendants have appealed therefrom.
Plaintiff, a Vermont corporation, owns and operates the Seaway Shopping Center in South Burlington, Vermont. Its principal stockholder and officer is Thomas Farrell, who developed the shopping center.
The Grand Union Stores, Inc., of Vermont, is also a Vermont corporation, and a wholly owned subsidiary of The Grand Union Company. The Grand Union company is a Delaware corporation with its principal office in East Paterson, New Jersey. The Grand Union Company is a guarantor of the performance of its subsidiary company under the lease here in question.
For the purposes of this opinion, Seaway Shopping Center is hereinafter referred to as "Seaway", The Grand Union Stores, Inc., of Vermont, as "Tenant", and The Grand Union Company as "P
…[truncated]
```

### `freelaw-val-199`

- tokens: 1,907
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 199

```text
137 F.3d 326
AVONDALE INDUSTRIES, INC., Petitioner,v.Rodney PULLIAM; Director, Office of Worker's CompensationPrograms, U.S. Department of Labor, Respondents.
No. 97-60569

Summary Calendar.
United States Court of Appeals,Fifth Circuit.
March 31, 1998.
Joseph J. Lowenthal, Jr., R. Scott Jenkins, Jones, Walker, Waechter, Poitevent, Carrere & Denegre, New Orleans, LA, for Petitioner.
Joseph Paul Demarest, Favret, Demarest, Russo & Lutkewitte, New Orleans, LA, for Pulliam.
Thomas O. Shepherd, Jr., Clerk, Benefits Review Bd., Washington, DC, Carol DeDeo, Assoc. Sol., U.S. Dept. of Labor, Dir., Office of Workers Comp. Programs, Washington, DC, for Director, Office of Worker's Compensation Programs, U.S. Dept. of Labor.
Petition for Review of an Order of the Benefits Review Board.
Before DUHE, DeMOSS and DENNIS, Circuit Judges.
DUHE, Circuit Judge:

1
Appellee injured his shoulder and sued Appellant, his former employer, for permanent and total disability payments under the Longshore and Harbor Workers' Compensation Act. The administrative law judge awarded him permanent, partial disability payments and calculated his wage earning capacity by averaging the hourly wage of five jobs which Appellant had found for Appellee. The Benefits Review Board affirmed. The res nova issue presented is the proper method of computing post-injury wage earning capacity when the employer locates more than one suitable job for the claimant. We affirm the ALJ's use of averaging.

2
* In May 1992, Rodney
…[truncated]
```

### `freelaw-val-204`

- tokens: 574
- 13-gram overlap with training text: 42.5267%
- source: `val.jsonl.zst` line 204

```text
COURT OF APPEALS
                                 EIGHTH DISTRICT OF TEXAS
                                      EL PASO, TEXAS
                                             §

  Leonardo Ramirez, § No. 08-19-00097-CR

                        Appellant, § Appeal from the

  v. § 41st District Court

  The State of Texas, § of El Paso County, Texas

                        State. § (TC# CR 20170D04632)

                                                §
                                           ORDER

       The Court GRANTS the Court Reporter’s third request for an extension of time within

which to file the Reporter’s Record until August 12, 2019. NO FURTHER REQUESTS

FOR EXTENSION OF TIME TO FILE THE REPORTER’S RECORD WIL BECONSIDERED

BY THIS COURT.

       It is further ORDERED that Bertha A. Prieto, Official Court Reporter for the 41st District

Court, for El Paso County, Texas, prepare the Reporter’s Record for the above styled and

numbered cause and forward the same to this Court on or before August 12, 2019.

       IT IS SO ORDERED this 29th day of July, 2019.

                                     PER CURIAM

Before McClure, C.J., Rodriguez and Palafox, JJ.
```

### `freelaw-val-278`

- tokens: 3,025
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 278

```text
611 S.E.2d 750 (2005)
272 Ga. App. 91
REYNOLDS
v.
The STATE.
No. A05A0768.
Court of Appeals of Georgia.
March 9, 2005.
Certiorari Denied June 6, 2005.
*751 George Jackson, Jackson & Schiavone, Savannah, for Appellant.
Daniel Craig, District Attorney, Henry Syms, Jr., Madonna Little, Assistant District Attorneys, for Appellee.
BLACKBURN, Presiding Judge.
Having pled guilty in 1999 to aggravated child molestation and child molestation, Gary Reynolds directly appeals the trial court's denial of his motion to set aside his sentence, which motion was filed more than four-and-one-half years after his unappealed sentence was entered. We hold that since Reynolds's sentence fell within the range of allowable sentences for the charged crimes, his claim that the sentence was void is without merit. Accordingly, his motion to set aside that sentence was untimely, depriving this direct appeal of jurisdiction. For this reason, we must dismiss the appeal.
*752 In March 1999, Reynolds was charged with six counts of child molestation[1] and one count of aggravated child molestation[2] arising out of conduct that took place between October 1992 and December 1994. In May 1999, he pled guilty to one count of child molestation and to one count of aggravated child molestation.
At the guilty plea hearing, attorneys for both sides, Reynolds himself, and the judge all believed and discussed that the range of punishment for the aggravated molestation count was ten to thirty years, with the range for th
…[truncated]
```

### `freelaw-val-325`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 16.9442%
- source: `val.jsonl.zst` line 325

```text
FILED
                      UNITED STATES COURT OF APPEALS DEC 06 2011

                                                                           MOLLY C. DWYER, CLERK
                             FOR THE NINTH CIRCUIT U.S. COURT OF APPEALS

RICHARD RAYMOND TUITE, No. 09-56267

               Petitioner - Appellant, D.C. No. 3:08-cv-01101-J-CAB
                                                  Southern District of California,
  v. San Diego

MICHAEL MARTEL, Warden,
                                                  ORDER
               Respondent - Appellee.

Before: NOONAN, BERZON, and CALLAHAN, Circuit Judges.

        The memorandum disposition filed on September 8, 2011 is hereby

withdrawn. A new disposition will be filed.

        The majority of the panel votes to deny the petition for rehearing. Judge

Callahan votes to grant the petition for rehearing. Judge Berzon votes to deny

petition for rehearing en banc and Judge Noonan recommends denying the petition

for rehearing en banc. Judge Callahan votes to grant the petition for rehearing en

banc.

        The full court has been advised of the petition for rehearing en banc, and no

judge of the court has requested a vote on whether to rehear the matter en banc.

Fed. R. App. P. 35.
 The petition for rehearing is DENIED and the petition for rehearing en banc

is DENIED.

      No further petitions for rehearing and for rehearing en banc will be

entertained.

                                         2
 FILED
       
…[truncated]
```

### `freelaw-val-336`

- tokens: 1,450
- 13-gram overlap with training text: 0.1391%
- source: `val.jsonl.zst` line 336

```text
22 B.R. 447 (1982)
In re Maris K. RINEER and Diane M. Rineer, Debtors.
Maris K. RINEER and Diane M. Rineer, Plaintiffs,
v.
BANK OF the NORTH SHORE, Defendant.
Bankruptcy Nos. 82 B 00044, 82 A 1250.
United States Bankruptcy Court, N.D. Illinois, E.D.
August 17, 1982.
E. Paul Rustin, Chicago, Ill., for plaintiffs.
Sherwin Willens, Wilmette, Ill., for defendant.

MEMORANDUM OPINION
FREDERICK J. HERTZ, Bankruptcy Judge.
This cause of action comes to be heard on a motion for summary judgment filed by the debtors, Maris and Diane Rineer (hereinafter referred to as plaintiffs) against the Bank of the North Shore (hereinafter referred to as North Shore) to rescind a security interest held by North Shore in the plaintiffs' home.
In May of 1978, North Shore financed plaintiffs' purchase of a 1978 Dodge motor home under a retail installment contract. Subsequently, the plaintiffs defaulted on the contract. North Shore notified the plaintiffs that the vehicle would be repossessed unless the arrearages were paid in full. Plaintiffs requested that North Shore refrain from repossessing the vehicle, and North Shore agreed, provided that the plaintiffs give North Shore a second mortgage lien on their home at 6922 Chestnut, Hanover Park, Illinois as additional collateral for the obligation existing under the retail installment contract. On June 3, 1980, the plaintiffs executed an addendum to their original contract which gave North Shore a second mortgage on their home. The plaintiffs executed 
…[truncated]
```

### `freelaw-val-358`

- tokens: 891
- 13-gram overlap with training text: 0.7964%
- source: `val.jsonl.zst` line 358

```text
434 So.2d 1031 (1983)
Rafael Humberto PALACIOS, Appellant,
v.
STATE of Florida, Appellee.
No. AO-373.
District Court of Appeal of Florida, First District.
July 22, 1983.
Rehearing Denied August 4, 1983.
*1032 Michael E. Allen, Public Defender, Glenna Joyce Reeves, Asst. Public Defender, Tallahassee, for appellant.
Jim Smith, Atty. Gen., Andrew Thomas, Asst. Atty. Gen., Tallahassee, for appellee.
ERVIN, Chief Judge.
Appellant, Rafael Humberto Palacios, appeals from a conviction for the offense of trafficking in marijuana, contending, inter alia, that the trial court erred in denying his motion to suppress physical evidence seized subsequent to a non-consensual search not incident to arrest. We agree and reverse.
The record discloses that Palacios was driving a rental truck north on Interstate 75 in Hamilton County at 4:00 a.m. on December 1, 1981, when he failed to stop at an agricultural inspection station. Inspector Davis, a uniformed officer on duty at the time, saw the truck by-pass the station and accordingly pursued it in an official marked car with blue lights flashing. He stopped the truck some 2 1/2 miles north of the station and then informed the driver, Palacios, first that he was required to stop at the station, and second that he needed to inspect the truck's cargo section. Palacios, a recent Cuban immigrant who speaks only Spanish, said, "No English." Davis again attempted to explain that he needed to inspect the rear of the truck and motioned to Palacios to open
…[truncated]
```

### `freelaw-val-376`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 376

```text
29 Wn. App. 461 (1981)
629 P.2d 912
THE STATE OF WASHINGTON, Respondent,
v.
DONALD R. WEDDEL, Appellant.
No. 4250-II.
The Court of Appeals of Washington, Division Two.
May 29, 1981.
Stephen Whitehouse, for appellant.
Patrick D. Sutherland, Prosecuting Attorney, and Chris Pomeroy, Deputy, for respondent.
REED, C.J.
Defendant Donald R. Weddel appeals his conviction of second degree burglary. We affirm.
On March 18, 1979, Larry and Jacqueline Wassman returned to their home in Lacey and discovered a gray Chevrolet Chevelle in their driveway with a young woman in the front seat. After the Wassmans had a brief conversation with the woman, who indicated that she thought their house was the residence of "the Hansons," a man they later identified as defendant Weddel came out from behind the house. He circled on foot to a vacant lot next to the house and then approached the vehicle, asking if the lot was for sale. After the man and woman left, Mr. Wassman, suspicious because of their inconsistent explanations for being at *463 the house, wrote down the Chevelle's license number, NET 900, and subsequently reported the incident to the police. There was no evidence, however, of any attempted entry to the Wassman residence.
On March 19, Paul and Wendy Johnson, returning from a shopping trip, arrived at their home located approximately seven-tenths of a mile from the Wassman residence. As the Johnsons pulled up to their mailbox across the street from their home, they noticed a gray Chevrole
…[truncated]
```

### `freelaw-val-41`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 41.2096%
- source: `val.jsonl.zst` line 41

```text
United States Court of Appeals
                          FOR THE EIGHTH CIRCUIT

                                  __________

                                  No. 02-3035
                                  __________

Dan McCarthy, as Parent and as Next *
Friend of his Minor Daughter, *
                                          *
              Plaintiff - Appellant, *
                                          * Appeal from the United States
       v. * District Court for the Western
                                          * District of Arkansas.
Ozark School District; Faye Boozman, *
in his Official Capacity as Director, *
State of Arkansas Department of Health; *
John Doe, 1 through 20, in their Official *
Capacities as Agents, Servants, *
Employees or Officials of the State of *
Arkansas, Department of Health, *
                                          *
              Defendants - Appellees. *

                                  ___________

                                  No. 02-3094
                                  ___________

Shannon Law, as Parent and Legal *
Guardian of her Minor Children Joey *
Law, Rob Law, and Claire Law; *
                                        *
            Plaintiff, *
                                        *
 Susan Brock, as Parent and Legal *
Guardian of her Minor Children Harley *
Brock, Mason Brock, Kathrine Brock *
and Michael Jarrell, *
                                       *
            Plaintiff - Appellant, *
                  
…[truncated]
```

### `freelaw-val-47`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 47

```text
274 Kan. 939 (2002)
58 P.3d 716
STATE OF KANSAS, Appellee,
v.
JAMES McINTOSH, Appellant.
No. 86,386.
Supreme Court of Kansas.
Opinion filed December 6, 2002.
*940 Paige A. Nichols, assistant appellate defender, argued the cause, and Reid T. Nelson, assistant appellate defender, Steven R. Zinn, deputy appellate defender, and Jessica R. Kunen, chief appellate defender, were with her on the briefs for appellant.
Keith E. Schroeder, district attorney, argued the cause, and Thomas R. Stanton, deputy district attorney, and Carla J. Stovall, attorney general, were with him on the briefs for appellee.
The opinion of the court was delivered by
LOCKETT, J.:
Defendant petitions for review from the Court of Appeals' affirmance of his convictions of rape, aggravated indecent liberties with a child, and two counts of aggravated criminal sodomy and his sentence of 316 months' imprisonment. Defendant claims (1) the trial court erred in finding that he failed to establish a compelling reason to require the victim to submit to an independent psychological examination; (2) the Court of Appeals erred in finding that a district court has no authority to order an independent physical examination of a victim in a criminal case; and (3) the trial court erred in admitting expert testimony.
The facts as set forth in the Court of Appeals' opinion provide sufficient background in this case. Further facts are incorporated in the opinion as necessary.
"McIntosh lived with Zoe D., his girlfriend, from Dece
…[truncated]
```

## Wikipedia (en)

59 documents in the test half; 10 shown.

### `wikipedia_en-val-1039`

- tokens: 1,039
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 1,039

```text
El tren de la muerte

El tren de la muerte ("The Death Train") refers to a network of Mexican freight trains that are utilized by U.S.-bound migrants to more quickly traverse the length of Mexico, also known as La Bestia ("The Beast") and El tren de los desconocidos ("The train of the unknowns"). It is estimated that yearly between 400,000 and 500,000 migrants, the majority of whom are from El Salvador, Guatemala, and Honduras, ride atop these trains in the effort to reach the United States. Although these trains (which transport products and materials including corn, cement, and minerals) are regarded as a free form of travel that allows migrants to avoid Mexico's numerous immigration checkpoints and 48 detention centers, the risks are high and many riders are left with life-altering injuries that limit their capacity to work.

As of May 9, 2014, train operators have banned the passengers from traveling by the train.

Passenger risks

Many of the dangers posed by this journey result from the train itself and the process of climbing aboard and getting off moving trains. Because migrants board between 10 and 15 trains during their 1450-mile journey, which typically begins in Arriaga, Chiapas, the chances of sustaining a major injury are high before they even arrive at Lechería station in Mexico City, which serves as a sort of halfway point before the train route scatters into various directions that head closer to different points on the U.S. border. Often, migrants fall aslee
…[truncated]
```

### `wikipedia_en-val-1089`

- tokens: 101
- 13-gram overlap with training text: 3.3708%
- source: `val.jsonl.zst` line 1,089

```text
Podocarpus steyermarkii

Podocarpus steyermarkii is a species of conifer in the family Podocarpaceae.
It is found only in Venezuela.

References

 Conifer Specialist Group 1998. Podocarpus steyermarkii. 2006 IUCN Red List of Threatened Species. Downloaded on 10 July 2007.

steyermarkii
Category:Least concern plants
Category:Taxonomy articles created by Polbot
```

### `wikipedia_en-val-1199`

- tokens: 172
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 1,199

```text
2nd Miyakibashevo

2nd Miyakibashevo (; , 2-se Miäkäbaş) is a rural locality (a village) in Miyakibashevsky Selsoviet of Miyakinsky District, Russia. The population was 56 as of 2010.

Geography
The village is located 12 km from Kirgiz-Miyaki, 12 km from Anyasevo and 56 km from the nearest railway station (Aksyonovo).

Ethnicity
The village is inhabited by Bashkirs and other.

Streets
 Tsentralnaya

References

External links
 2nd Miyakibashevo on komandirovka.ru

Category:Rural localities in Bashkortostan
```

### `wikipedia_en-val-1314`

- tokens: 637
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 1,314

```text
Privy Council of Tonga

The Privy Council of Tonga is the highest ranking council to advise the Monarch in the Kingdom of Tonga. It is empowered to advise the King in his capacity as Head of State and Fountain of Justice under the provisions of Clause 50 ( 1 ) of the Constitution of Tonga:

" Clause 50 (1) The King shall appoint a Privy Council to provide him with advice. The Privy Council shall be composed of such people whom the King shall see fit to call to his Council."

Membership
Members of the Privy Council are appointed by the King of Tonga who is its Chairman. The Council has three types of members:
 Regular Members-these are the majority.
 Members who hold their position by virtue of an office they occupy
 The Law Lords

The Lord Chancellor, the Lord President of the Supreme Court and the Attorney General are automatically members of the Privy Council. The constitution doesn't set a limit on the number of members who sit on the Council and this is left to the discretion of the Monarch.

Judicial functions
The King in Privy Council has the authority to make appointments to most posts in the judicial branch of government. One of the primary goals of the constitutional reforms of 2010 was to ensure the separation of the executive, legislative and judicial branches of government. A significant result of these reforms and constitutional amendments was the removal of the King from the executive power. Executive power was transferred to the cabinet. The drafters of the 201
…[truncated]
```

### `wikipedia_en-val-217`

- tokens: 887
- 13-gram overlap with training text: 0.4571%
- source: `val.jsonl.zst` line 217

```text
Denny Landzaat

Denny Domingues Landzaat (known as Denny Landzaat, , born 6 May 1976) is a Dutch former footballer who mostly played as a defensive midfielder.

Early life
Landzaat was born and raised in Amsterdam. He is of Moluccan descent.

Club career

Early career
Landzaat was educated in Ajax's youth academy, but only played one league match for the club before moving on to have lengthy spells with MVV, Willem II and AZ. He was AZ's captain in the 2005–06 season, as they finished second in the Eredivisie.

Wigan Athletic
Landzaat joined Premier League club Wigan Athletic on 18 July 2006 for an undisclosed fee, thought to be £2.5 million. He signed a three-year contract with the club. He scored his first goal for Wigan against Reading in a 2–3 loss on 30 January 2007. He followed this with a 30-yard strike at the Emirates Stadium in a 1–2 defeat to Arsenal on 11 February. On 18 August 2007, Landzaat converted a penalty against Sunderland to score his first home goal for Wigan at the JJB Stadium. He also scored the first goal in Wigan's 5–3 win over local rivals Blackburn Rovers.

Feyenoord
On 25 January 2008, Landzaat returned to the Netherlands to join Feyenoord for a £1 million transfer fee. He signed a three-and-a-half-year contract with the club. He scored his first goal for Feyenoord on his debut, in the 3–3 draw against Heracles on 24 February 2008.

Twente
After his contract with Feyenoord expired, Landzaat signed a one-year deal with Twente in August 2010, which w
…[truncated]
```

### `wikipedia_en-val-267`

- tokens: 463
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 267

```text
Ariel S. Ballif

Ariel Smith Ballif, Sr. (December 9, 1901 – May 11, 1995) was a professor of sociology at Brigham Young University (BYU), mayor of Provo, Utah and a leader in The Church of Jesus Christ of Latter-day Saints (LDS Church).

Ballif was born in Logan, Utah to John Lyman Ballif and his wife, the former Emma Smith. In 1925 Ballif married Artemesia "Arta" Romney, who was a daughter of George S. Romney and a sister of Marion G. Romney. They had five children, including Ariel S. Ballif Jr., Jae R. Ballif and Bonnie Ballif-Spanvill, who also became professors in Utah.

Ballif earned his bachelor's degree from BYU and then an MA and Ph.D. from the University of Southern California. From 1927-1930 Ballif served with his wife as a missionary in New Zealand, serving as principal of the Maori Agricultural College for most of that time.

Ballif joined the faculty of BYU in 1938 and served as chairman of the sociology department for a number of years.

Ballif served as a bishop, a Stake President and a Stake Patriarch. He also served as president of the New Zealand Mission from 1955-1958, thus being mission president at the time the New Zealand Temple was built.

Ballif was elected to the Provo City Council in 1958, and from 1960-1961 he was mayor of Provo.

Notes

Sources
listing of New Zealand Mission Presidents
Political Graveyard listing
Time Magazine article
BYH alumni listing

Category:1901 births
Category:1995 deaths
Category:American Mormon missionaries in New Zealand
…[truncated]
```

### `wikipedia_en-val-420`

- tokens: 67
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 420

```text
E2A

E2A may refer to:
E2A peptide, a 2A self-cleaving peptides.
E2A immunoglobulin enhancer-binding factors E12/E47.
Chūgoku Expressway and Kanmon Bridge, route E2A in Japan.
```

### `wikipedia_en-val-578`

- tokens: 238
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 578

```text
Cordwood Point

Cordwood Point is a promontory of Cheboygan County that extends out into Lake Huron. Located 6.5 miles (10.5 km) east of Cheboygan, it marks the east end of the South Channel, the southernmost navigational channel of the Straits of Mackinac. The point has been subdivided into real estate for cabins and summer residences. U.S. Route 23 serves the point and its small settlement.

The point's name reflects the need of pioneer steamboats to be fueled with cordwood. Small steamboats would stop here at now-long-vanished wharves and fuel up. Later technology moved the primary fuel supply of Lake Huron steamboats from wood to coal, and the cordwood trade dwindled and died. When the county was organized into townships, Cordwood Point became part of Benton Township.

Poe Reef Light, the midchannel lighthouse in the South Channel, stands 2.6 miles northwest of Cordwood Point.

References

Category:Landforms of Cheboygan County, Michigan
Category:Peninsulas of Michigan
```

### `wikipedia_en-val-620`

- tokens: 608
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 620

```text
Girl Mistress

is a 1980 Japanese pink film directed by Banmei Takahashi.

Synopsis
An older yakuza man falls in love with Seru, a high school girl. When he is put in prison, Seru begins working as a prostitute to earn money for the gangster's parole. During her yakuza lover's incarceration, Seru gains a new, young boyfriend. The yakuza discovers the new boyfriend after he is released from prison. Realizing that she will have a better life with her new boyfriend who is not associated with the yakuza, he sacrifices his love for Seru and gives her up.

Cast
 Cecile Gōda (豪田路世留) as Seru
 Satoshi Miyata (宮田諭) as Seru's younger boyfriend
 Shirō Shimomoto (下元史郎) as yakuza in love with Seru
 Naomi Oka (丘なおみ)
 Maria Satsuki (五月マリア)
 Ren Ōsugi (大杉漣)

Background and critical appraisal
Along with Mamoru Watanabe and Genji Nakamura, Banmei Takahashi was known as one of the "Three Pillars of Pink" before he made Girl Mistress. He was known for his stylistically unique approach to the genre which brought college students back to pink film theaters at this time, when Nikkatsu's Roman Porno series was beginning to lose its popularity among this audience.

In their Japanese Cinema Encyclopedia: The Sex Films, Thomas and Yuko Mihara Weisser give Girl Mistress three-and-a-half out of four stars. Without stating what award the film won, they note that it is an "award-winning motion picture". Director Takahashi had already made a name for himself in the pink film through his films at Kōji Wakamat
…[truncated]
```

### `wikipedia_en-val-944`

- tokens: 72
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 944

```text
Niphorycta hemipercna

Niphorycta hemipercna is a moth in the family Xyloryctidae. It was described by Alexey Diakonoff in 1954. It is found in New Guinea.

References

Category:Xyloryctidae
Category:Moths described in 1954
```

## USPTO Backgrounds

33 documents in the test half; 10 shown.

### `uspto_backgrounds-val-14`

- tokens: 511
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 14

```text
1. Field of the Invention
The present invention relates generally to the field of semiconductor fabrication and, more particularly, to the field of fabricating p-channel and n-channel transistors with different characteristics on a common substrate.
2. Description of Related Art
In complementary metal oxide semiconductor (CMOS) fabrication, p-channel and n-channel transistors are fabricated on the same semiconductor substrate. To achieve transistors of both polarities (conductivity types), it is necessary that at least some process is steps differentiate between p-type and n-type transistors. Separate implant steps, for example, are needed to define n-well and p-well structures and to dope the source/drain regions of n-channel and p-channel transistors. Whenever possible, however, it is generally desirable to use a single process step to define transistor features regardless of the transistor type. Single process steps imply a single mask step, which is always desirable to reduce load on the photolithography processing. Moreover, a single step generally minimizes undesirable variations between the p-channel and n-channel transistors. Imagine, for example, that a particular design has been optimized under the assumption that the thickness of the gate oxide (or other dielectric) is the same on n-channel and p-channel transistors. The best way to ensure that the assumption is correct is to form the relevant feature for p-channel and n-channel transistors simultaneously.
In some 
…[truncated]
```

### `uspto_backgrounds-val-192`

- tokens: 550
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 192

```text
Handling huge volumes of data on a daily basis is a task that most organizations have to deal with. Such organizations have been storing huge volumes of data for decades, but now with the availability of new techniques for analyzing those huge data sets, organizations seek to improve their operational efficiency. Data sets today aren't merely larger than the older data sets, but also significantly more complex, for example, unstructured and semi-structured data generated by sensors, web logs, social media, mobile communication, and customer service records.
There are many software frameworks to store and analyze large volumes of data in a massively parallel scale. Apache Hadoop is an example and often cited in many journals, publications, blogs, and other technical articles for massively parallel processing system. It is now known to be the de-facto technology platform for supporting storage of massive amounts of heterogeneous data and processing them.
The Hadoop Distributed File System (HDFS) for data storage and its specialized distributed programming model ‘MapReduce’ for data processing, across relatively inexpensive commodity hardware, may be leveraged for mixing and matching data from many disparate sources and reveal meaningful insights.
However, Hadoop as a technology has several limitations. First, organizations are interested in ‘interactive analytics’, a solution requiring faster time-to-insight when compared to the time it takes for a MapReduce job to execute and 
…[truncated]
```

### `uspto_backgrounds-val-20`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 20

```text
1. Field of the Invention
The present invention relates to an improved dispensing apparatus. More particularly, a dispenser that incorporates a timing means in conjunction with audio and visual output to assist the user in proper washing techniques for compliance with recommended guidelines and to monitor the number of usages.
2. Background Art
Each year, millions of reported illnesses and serious infections are attributable to improper hand washing. The unreported cases are estimated to be much higher. Food borne illness kills over 10,000 people each year, and 70% of the outbreaks originate in food service sector. The passage of viral and bacterial contaminants result from physical contact with an infected source and are carried from one site to another with each successive physical contact.
The problem is most evident in hospital and related medical establishments, as well as those businesses associated with preparing and distributing food and food products. A person that handles a single contaminated source will spread the contaminant to every person, article and surface touched by that person. The subsequent contaminated sources represent additional contamination sites that spread the contaminant. The liability of contamination or illness caused by inadequate washing techniques is very high. And, a single food borne illness can tarnish a long-standing reputation and wreak financial havoc.
Proper washing of hands has been demonstrated to kill the contaminants and prevent t
…[truncated]
```

### `uspto_backgrounds-val-309`

- tokens: 809
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 309

```text
1. Field of the Invention
This invention generally relates to the field of electronic data storage, analysis, and recovery. Specifically, the invention relates to a system used for arranging and organizing data backup, computing system operation data, storing system data, monitoring and analyzing collected historical system data, predicting a future system occurrence, taking the appropriate steps to notify a specified party of a future occurrence, and taking the appropriate steps to correct or prevent a future occurrence.
2. Description of Related Art
Data backup is often recognized as a necessity for nearly all computer-based systems. Businesses and other enterprises that rely heavily on computer systems are often paralyzed in the event of a system failure or a data loss. These failures can lead to lost profits and high repair and recovery costs. Furthermore, many computer systems handle sensitive and valuable data, which holds significant value.
Because of the importance and value of continuous system operation and reliable data storage, a number of methods have been devised for data backup. Many of these methods employ large data storage media (such as tapes, high-capacity hard drives, etc.) that are used to periodically transcribe a system's body of data.
These backup systems, while effective in copying large amounts of data, have a number of shortcomings. Firstly, many systems do not employ a media management system, which tracks the appropriate media for a given backup.
…[truncated]
```

### `uspto_backgrounds-val-310`

- tokens: 458
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 310

```text
Bromine is used in a wide range of industries. For example, bromine is used in the manufacture of flameproofing agents, 1,2-dibromoethane (CH2BrCH2Br) (which is used as a petrol additive to prevent lead being deposited in cylinders), compounds used in photography (e.g. silver bromide, AgBr, which is the light sensitive material in film), dyestuffs and drugs; in the analytical laboratory in testing for unsaturation in organic compounds, where bromine adds across the multiple bonds of unsaturated compounds, as a disinfectant; and in making fumigants, water purification compounds, dyes, medicinals; and sanitizers. Bromine can be produced by oxidation of bromides using hydrogen peroxide as the oxidant. For example, the following reaction is suitable: H2O2+2HBrBr2+2H2O (Reaction (1)). Bromine can also be produced by oxidation of bromides using chlorine as the oxidant. For example, the following reaction is suitable: 2NaBr+Cl2Br2+2NaCl (Reaction (2)).
U.S. Pat. No. 5,266,295 describes use of a strong acid, such as sulfuric or phosphoric acid, to improve effectiveness when hydrogen bromide is oxidized to bromine using hydrogen peroxide as the oxidant. However, process economics are affected by the addition of an acid; and in some cases an add source is not readily available. Each of Reactions (1) and (2) could benefit from the addition of catalysts to increase the percent conversion of bromide to bromine. Ammonium molybdate ((NH4+)2MoO4−) is a known oxidation catalyst to allow iodom
…[truncated]
```

### `uspto_backgrounds-val-522`

- tokens: 633
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 522

```text
The present invention relates generally to apparatuses and methods for controlling a length of a brewing cycle during which time a brewer brews a beverage. The present invention more specifically relates to an apparatus and method for controlling a length of a brewing cycle during which time a brewer brews a beverage, where an initial brew time which is stored in a controller can be adjusted relatively easily.
Some automatic brewers which brew hot beverages, such as coffee or tea, provide that the length of a brewing cycle can be programmed into the brewer so that each time the brewer performs a brewing cycle, generally the same volume of beverage is brewed.
For example, some automatic brewers provide a controller which generally controls the brewing operation and the length of the brewing cycle. Additionally, a warmer switch, a brew button and a run/program switch are provided on the brewer. To initially set the length of the brewing cycle of the brewer, a user switches on the warmer switch causing a warmer in the brewer to turn on, then switches the run/program switch from a "run" setting to a "program" setting. Then, the user presses the brew button to begin brewing, and after allowing the brewing to continue until the desired amount of beverage has been brewed by the brewer, the user turns off the warmer switch or presses the brew button a second time. The controller programs the brewing cycle to be the length of time between the beginning of the brewing and the switching
…[truncated]
```

### `uspto_backgrounds-val-561`

- tokens: 485
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 561

```text
1. Field of the Invention
The present invention relates generally to gaming, and more particularly to a device and method for dispensing game tickets for playing games of chance for monetary prizes.
2. Description of the Prior Art
Gaming is a widely popular form of entertainment and an economically important industry. State-run lotteries and other games of chance produce significant amounts of revenue for funding various socially beneficial activities such as education, economic development, etc.
In the private sector, games of chance are often used for both fundraising and entertainment purposes. For example, various charitable, social and fraternal organizations purchase sets of game materials consisting of game cards and tickets. Game cards typically have break-open windows or scratch-off areas for concealing winning and losing symbols prior to purchase. Game tickets are typically folded and sealed for concealing winning and losing symbols prior to purchase. Players unfold them to reveal the symbols as the games are played. Winning game symbols typically entitle the players to monetary prize amounts. The games can be designed with predetermined payout percentages. The game operators are thus assured of predetermined profit amounts after all of the cards or tickets are sold and all of the prizes are awarded.
The prior art includes various devices for packaging, promoting, displaying, and dispensing game cards and tickets. For example, folded-and-sealed tickets have for many
…[truncated]
```

### `uspto_backgrounds-val-606`

- tokens: 4,096  (capped at 4,096)
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 606

```text
The present invention relates to high-performance radiation sensitive resist compositions and their use in multilayer lithography processes to fabricate semiconductor devices. Specifically, the present invention is concerned with negative-tone silicon-containing resist compositions based on an acid catalyzed crosslinking of aqueous base soluble silicon-containing polymers. The resist composition of the present invention can be used as the top imaging layer in a multilayer, including bilayer, technique to fabricate semiconductor devices using various irradiation sources, such as mid-ultraviolet (UV), deep-UV (for example 248 nm, 193 nm and 157 nm), extreme UV, X-ray, e-beam and ion-beam irradiation.
In the manufacture of patterned devices such as semiconductor chips and chip carriers the steps of etching different layers which constitute the finished product are among the most critical and crucial steps involved.
In semiconductor manufacturing, optical lithography has been the main stream approach to pattern semiconductor devices. In typical prior art lithography processes, UV light is projected onto a silicon wafer coated with a layer of photosensitive resist through a mask that defines a particular circuitry pattern. Exposure to UV light, followed by subsequent baking, induces a photochemical reaction which changes the solubility of the exposed regions of the photosensitive resist. Thereafter, an appropriate developer, typically an aqueous base solution, is used to selective
…[truncated]
```

### `uspto_backgrounds-val-790`

- tokens: 769
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 790

```text
1. Field of the Invention
This invention relates to an ultrasonic diagnostic apparatus which transmits an ultrasonic beam from an ultrasonic probe to a subject, such as a biological body, receives the echoes from the subject, and obtains ultrasonic image data on the subject, and more particularly to an ultrasonic diagnostic apparatus and an ultrasonic diagnostic method which adjust a transmission voltage sent to an ultrasonic probe to the optimum value.
2. Description of the Related Art
With an ultrasonic diagnostic apparatus, an ultrasonic probe is brought into contact with a subject, such as a biological body. In this state, the ultrasonic probe transmits an ultrasonic beam to the inside of the subject and receives the echoes from the inside of the subject, thereby acquiring ultrasonic image data on the subject. The ultrasonic probe transmits an ultrasonic beam of acoustic power corresponding to a transmission voltage specified by a system control unit of the ultrasonic diagnostic apparatus. As for the transmission voltage to the ultrasonic probe, a transmission voltage preset within an acoustic power limit range by the system control unit is set as the maximum transmission voltage.
The ultrasonic beam is adjusted according to the type of subject, such as an unborn baby or an internal organ, so as not to transmit high acoustic power to the subject. The acoustic power of the ultrasonic beam is adjusted by the user manually operating an acoustic power adjustment switch provid
…[truncated]
```

### `uspto_backgrounds-val-916`

- tokens: 609
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 916

```text
The neuronal ceroid lipofuscinoses (NCLs) are a group of closely related hereditary neurodegenerative disorders which affect infants, children and adults, and which occur at a frequency of between 2 and 4 in 100,000 live births (1, 2). Most forms of NCL afflict children and their early symptoms and disease progression tend to be similar. Initial diagnosis is frequently based upon visual problems, behavioral changes and seizures. Progression is reflected by a decline in mental abilities, increasingly severe and untreatable seizures, blindness and loss of motor skills while further progression can result in dementia or a vegetative state. There is no effective treatment for NCL and all childhood forms are eventually fatal. Several forms of NCL are differentiated according to age of onset, clinical pathology and genetic linkage. These include infantile NCL (INCL, CLN1), classical late infantile NCL (LINCL, CLN2), juvenile NCL (JNCL, CLN3) adult NCL (CLN4), two variant forms of LINCL (CLN5 and CLN6) and possibly other atypical forms (1.3). The molecular bases for two of these forms of NCL have recently been identified by positional cloning. Mutations in palmitoyl protein thioesterase (PPT), which removes the lipid moiety from acylated proteins, results in INCL (4). JNCL results from mutations in the CLN3 gene product, a 48 kDa protein of currently unknown function (5). The identity of the molecular lesion in LINCL has remained elusive although the disease gene has recently been m
…[truncated]
```

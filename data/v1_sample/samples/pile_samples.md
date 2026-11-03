# Pile hand-check sample

3 random documents per subject from the **test** halves, first 1,500 characters of the cleaned text. Seeded from the data seed, so a rebuild shows the same documents.

**What to check:** the text reads like the subject its label claims; cleaning has not mangled it (code keeps its indentation, prose keeps its paragraphs); nothing looks like boilerplate repeated across documents; `ngram_overlap` is low except where the subject is self-overlapping by nature (`Github`, `FreeLaw`).

## Pile-CC

41 documents in the test half; 3 shown.

### `pile_cc-val-116`

- tokens: 326
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 116

```text
We all know that RiRi and Breezy had one of the most colorful history among celebrity couples. The pair had a roller coaster romance and have broken up and rekindled their relationship a couple of times before permanently calling it quits in 2014. Now some fans are panicking that Rihanna maybe missing her ex-boyfriend and could rekindle their old flame.

The Bajan pop beauty posted a pic of herself a few weeks back and captioned it, “When you hang up on em, then call right back. #firstofallimcrazy #secondofalliwasntdone.” Chris Brown has a song on his new album Heartbreak On a Full Moon titled “Other Ni**as” where he sing some similar lines.

“Oh girl, why you gotta be like that? (Girl, like that) / Why gotta hang up on me then you call right back? (Back) / How you compare me to them ni**as that you gave your heart to? (Heart to),” Chris Brown sings. Rihanna made her Instagram post a few days before Brown drop the album and some fans are now saying that he might have given her a copy of the project before it was released, which means that they are secretly communicating with each other. On the other hand, it could be just share coincidence that RiRi made a quote identical to Breezy’s lyrics just a few days before he drop an album, just how likely is that. Listen to the full song “Other Ni**as” below.
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

### `pile_cc-val-54`

- tokens: 51
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 54

```text
BookGoodies host Deborah Carney is joined by indie author PJ Sharon to discuss why she chose to publish independently and share her tips on becoming a successfully published author. Some of the resources PJ shared are below, there are many more great tips in the podcast.
```

## Github

18 documents in the test half; 3 shown.

### `github-val-1`

- tokens: 72
- 13-gram overlap with training text: 0.0000%
- source: `val.jsonl.zst` line 1

```text
### Solution for "Download of Code Without Integrity Check" challenge

This challenge showcases a situation common to software deployments where an update server is being used but integrity checks are no in place in order to validate the software has not been tampered with.

Only thing required to do in order to pass is changing the update server to `evil.bad`.
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

## PubMed Central

7 documents in the test half; 3 shown.

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

## FreeLaw

10 documents in the test half; 3 shown.

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

59 documents in the test half; 3 shown.

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

33 documents in the test half; 3 shown.

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

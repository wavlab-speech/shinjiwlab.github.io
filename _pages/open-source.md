---
layout: page
title: Open-source
permalink: /open_source

nav: true
order: 5
---

Our lab has led and participated in the development of several open-source toolkits, projects, and datasets. Some selected ones are listed below.

### Softwares

<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://github.com/espnet/espnet">
        <img src="{{ site.baseurl }}/assets/img/espnet_logo1.png" width="150" />
      </a>
</td>
<td>
  <strong>ESPnet</strong> is an end-to-end speech processing toolkit, with a broad coverage of speech recognition, text-to-speech, speech enhancement/separation, and speech translation. ESPnet uses pytorch as a main deep learning engine, and also follows Kaldi style data processing, feature extraction/format, and recipes to provide a complete setup for speech recognition and other speech processing experiments.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://github.com/wavlab-speech/versa">
        <img src="{{ site.baseurl }}/assets/img/blog/versa-light-char.png" width="150" />
      </a>
</td>
<td>
  <strong>VERSA</strong> (Versatile Evaluation of Speech and Audio) is a comprehensive toolkit for evaluating speech and audio quality. It provides seamless access to over 80 evaluation/profiling metrics with 10x variants, enabling researchers and developers to assess audio quality through multiple dimensions.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25" style="display:table-cell; vertical-align:middle; text-align:center">
      <a href="https://github.com/kaldi-asr/kaldi">
        <img src="{{ site.baseurl }}/assets/img/kaldi-logo.png" width="100" />
      </a>
</td>
<td>
  <strong>Kaldi</strong> is a toolkit for speech recognition written in C++ and licensed under the Apache License v2.0. Kaldi is intended for use by speech recognition researchers.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://github.com/s3prl/s3prl">
        <img src="{{ site.baseurl }}/assets/img/S3PRL-logo.png" width="150" />
      </a>
</td>
<td>
  This is an open source toolkit called <strong>s3prl</strong>, which stands for <strong>S</strong>elf-<strong>S</strong>upervised <strong>S</strong>peech <strong>P</strong>re-training and <strong>R</strong>epresentation <strong>L</strong>earning. Self-supervised speech pre-trained models are called <strong>upstream</strong> in this toolkit, and are utilized in various <strong>downstream</strong> tasks.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25" style="display:table-cell; vertical-align:middle; text-align:center">
      <a href="https://github.com/freewym/espresso">
        <img src="{{ site.baseurl }}/assets/img/espresso_logo.png" width="100" />
      </a>
</td>
<td>
  <strong>Espresso</strong> is an open-source, modular, extensible end-to-end neural automatic speech recognition (ASR) toolkit based on the deep learning library PyTorch and the popular neural machine translation toolkit fairseq. Espresso supports distributed training across GPUs and computing nodes, and features various decoding approaches commonly employed in ASR, including look-ahead word-based language model fusion, for which a fast, parallelized decoder is implemented.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25" style="display:table-cell; vertical-align:middle; text-align:center">
      <a href="https://github.com/SJTMusicTeam/Muskits">
        <img src="{{ site.baseurl }}/assets/img/muskit_logo.png" width="200" />
      </a>
</td>
<td>
  <strong>Muskits</strong>  is an open-source music processing toolkit, currently focus on benchmarking the end-to-end singing voice synthesis and expect to extend more tasks in the future. Muskit employs pytorch as a deep learning engine and also follows ESPnet and Kaldi style data processing, and recipes to provide a complete setup for various music processing experiments.
</td></tr>
</table>
<hr />


### Projects

<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="{% post_url 2024-01-01-owsm %}">
        OWSM
      </a>
</td>
<td>
  <strong>Open Whisper-style Speech Models</strong> (<strong>OWSM</strong>, pronounced as "awesome") are a series of speech foundation models developed by WAVLab at Carnegie Mellon University. We reproduce Whisper-style training using publicly available data and our open-source toolkit ESPnet. By publicly releasing data preparation scripts, training and inference code, pre-trained model weights and training logs, we aim to promote transparency and open science in large-scale speech pre-training.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="{% post_url 2024-06-30-xeus %}">
        XEUS
      </a>
</td>
<td>
  <strong>XEUS</strong> (pronounced “Zeus”) is an open-source speech foundation model trained on nearly 1.1 million hours of unlabeled speech data across 4,057 languages. XEUS sets the new state-of-the-art on the ML-SUPERB multilingual speech recognition benchmark, while also achieving strong results on different tasks on the English-only SUPERB evaluations. We open-source XEUS’ checkpoints, along with our training code and 4,000+ language speech data in this project page.
</td></tr>
</table>
<hr />


### Datasets

<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://chimechallenge.github.io/chime6/">
        <img src="{{ site.baseurl }}/assets/img/chime-logo.png" width="150" />
      </a>
</td>
<td>
  Following the success of the 1st, 2nd, 3rd, 4th and 5th CHiME challenges, we are pleased to announce the 6th <strong>CHiME</strong> Speech Separation and Recognition Challenge (CHiME-6). The new challenge will consider distant multi-microphone conversational speech diarization and recognition in everyday home environments. Speech material was elicited using a dinner party scenario with efforts taken to capture data that is representative of natural conversational speech.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://github.com/mispchallenge/MISP2021-AVSR">
        AVSR (MIPS2021)
      </a>
</td>
<td>
  <strong>Audio-Visual Speech Recognition (AVSR)</strong> corpus of MISP2021 challenge, a large-scale audio-visual Chinese conversational corpus consisting of 141h audio and video data collected by far/middle/near microphones and far/middle cameras in 34 real-home TV rooms. To our best knowledge, our corpus is the first distant multi-microphone conversational Chinese audio-visual corpus and the first large vocabulary continuous Chinese lip-reading dataset in the adverse home-tv scenario.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://github.com/mispchallenge/MISP2021-AVWWS">
        AVWWS (MIPS2021)
      </a>
</td>
<td>
  <strong>Audio-Visual Wake Word Spotting (AVWWS)</strong> concerns the identification of predefined wake word(s) in utterances. ‘1’ indicates that the sample contains wake word, and ‘0’ indicates the opposite. For more information, please refer to the MISP Challenge task 1 description.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://datasets.kensho.com/datasets/spgispeech">
        SPGISpeech
      </a>
</td>
<td>
  <strong>SPGISpeech</strong> is a corpus of 5,000 hours of professionally-transcribed financial audio. In contrast to previous transcription datasets, SPGISpeech contains a broad cross-section of L1 and L2 English accents, strongly varying audio quality, and both spontaneous and narrated speech. The transcripts have each been cross-checked by multiple professional editors for high accuracy and are fully formatted, including capitalization, punctuation, and denormalization of non-standard words.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="https://github.com/SpeechColab/GigaSpeech">
        GigaSpeech
      </a>
</td>
<td>
  <strong>GigaSpeech</strong> is an evolving, multi-domain English speech recognition corpus with 10,000 hours of high quality labeled audio suitable for supervised training, and 40,000 hours of total audio suitable for semi-supervised and unsupervised training.
</td></tr>
</table>
<hr />

<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="http://www.openslr.org/89/">
        ASR corpus for endangered language documentation (Yoloxóchitl Mixtec)
      </a>
</td>
<td>
  Substantive material of <strong>Yoloxóchitl Mixtec</strong> speech corpus (Glottocode: yolo1241 | ISO 639-3 = xty) presented here was brought together over ten years by Jonathan D. Amith (PI) and Rey Castillo García, a native speaker linguist from the community of Yoloxóchitl. The corpus is designed for ASR research in endangered language documentation.
</td></tr>
</table>
<hr />


<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="http://www.openslr.org/89/">
        ASR and ST corpus for endangered language documentation (Puebla Nahuatl)
      </a>
</td>
<td>
  The substantive material of <strong>Puebla Nahuatl</strong> speech corpus was gathered over ten years by Jonathan D. Amith (PI) and a team of native-speaker colleagues who have participated in the project for many years, one from its inception in 2009. The corpus is designed for ASR & MT research in endangered language documentation.
</td></tr>
</table>
<hr />


<table cellspacing="0" cellpadding="0">
<tr>
<td class="col-sm w-25">
      <a href="http://www.openslr.org/107/">
        ASR corpus for endangered language documentation (Totonac)
      </a>
</td>
<td>
  The substantive material of <strong>Totonac</strong> from the northern sierras of Puebla and adjacent areas of Veracruz were compiled starting in 2016 by Jonathan D. Amith and continue to the present as part of a joint effort by Amith and Osbel López Francisco, a native speaker biologist from Zongozotla.
</td></tr>
</table>
<hr />


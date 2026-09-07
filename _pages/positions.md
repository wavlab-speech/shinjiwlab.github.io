---
layout: page
permalink: /positions/
title: Positions
nav: true
order: 9
---

<style>
  .pos-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin: 1.5rem 0 2rem;
    padding: 0;
    list-style: none;
  }
  .pos-nav a {
    display: inline-block;
    border: 1px solid var(--pos-border);
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.9rem;
    color: var(--global-text-color);
    text-decoration: none;
  }
  .pos-nav a:hover,
  .pos-nav a:focus {
    border-color: var(--global-theme-color);
    color: var(--global-theme-color);
  }

  /* Steps to take, as a checklist look without any form controls. The old
     "- [ ]" markdown produced 14 disabled checkboxes: they invited a click,
     did nothing, and a screen reader read every one as unavailable. */
  .pos-steps { list-style: none; padding-left: 1.6rem; }
  .pos-steps > li {
    position: relative;
    margin-bottom: 0.55rem;
    line-height: 1.6;
  }
  .pos-steps > li::before {
    content: "\2610";                   /* an empty box glyph, decoration only */
    position: absolute;
    left: -1.6rem;
    color: var(--global-theme-color);
    font-size: 1.05rem;
    line-height: 1.5;
  }
  .pos-steps ul { margin-top: 0.4rem; }

  /* The site navbar is fixed and about 81px tall. Without this, clicking a
     chip lands the heading underneath the navbar, out of sight. */
  #postdoc, #phd, #collaborator, #visiting, #faq { scroll-margin-top: 6rem; }

  .pos-status {
    border-left: 3px solid var(--global-theme-color);
    background-color: var(--pos-surface);
    border-radius: 0 6px 6px 0;
    padding: 0.7rem 1rem;
    margin: 0.8rem 0 1.2rem;
  }

  .pos-faq details {
    border-bottom: 1px solid var(--pos-border);
    padding: 0.7rem 0;
  }
  .pos-faq summary {
    cursor: pointer;
    font-weight: 600;
    line-height: 1.5;
  }
  .pos-faq details[open] summary { margin-bottom: 0.6rem; }
  .pos-faq details > p,
  .pos-faq details > ul { font-size: 0.95rem; line-height: 1.65; }

  /* al-folio maps --global-text-color-light to the body colour in dark mode,
     so define these two locally instead of leaning on it. */
  :root { --pos-border: rgba(0, 0, 0, 0.14); --pos-surface: rgba(0, 0, 0, 0.03); }
  html[data-theme='dark'] { --pos-border: rgba(255, 255, 255, 0.18); --pos-surface: rgba(255, 255, 255, 0.05); }
</style>

Thank you for considering working with us!

Our lab has open and collaborative minds and often has various opportunities, including postdocs, visitors, and Ph.D. students. 
We want applicants to have solid fundamentals and interests in one or more of the following topics:

- Automatic speech recognition
- Speech enhancement and separation
- Spoken language understanding
- Machine learning for speech and language processing

Solid programming skills and open-source experiences are also preferred.

However, we also consider the research diversity. We're interested in expertise outside the above topics or other unique experiences, which can be applied to speech and audio problems.

Please see the following for details of each application category.

<ul class="pos-nav">
  <li><a href="#postdoc">Postdoc</a></li>
  <li><a href="#phd">Ph.D.</a></li>
  <li><a href="#collaborator">WAVLab Collaborator</a></li>
  <li><a href="#visiting">Visiting Positions</a></li>
  <li><a href="#faq">FAQ</a></li>
</ul>

### Postdoc
{: #postdoc}

<div class="pos-status" markdown="1">
Currently, we don't have an opening position, but if you really want to work with us, please contact us.
</div>

If you're interested in the position, we suggest you to have the following actions. **Note that we would not respond to all applications.**

- Please email your CV to shinjiw@ieee.org with the subject **"WAVLab postdoc applications"**.
- If you do not put it in the subject, we regard that you do not thoroughly investigate our lab's activities on this webpage, and unfortunately, we may not respond to this email.
- Note that your CV will be shared with other lab members (but we do not distribute it outside).
- Please check our publications and find matches in advance. We really care about it.
- Please clarify your available term. This is very important for the postdoc application.
{: .pos-steps}

### Ph.D.
{: #phd}

- Please submit your application through the [CMU SCS graduate application portal](https://admissions.scs.cmu.edu/portal/apply_gr). Unfortunately, we may not respond to a direct email about the Ph.D. application.
{: .pos-steps}

### WAVLab Collaborator
{: #collaborator}

- We provide training and research opportunities to students who are interested in speech processing and want to collaborate with us.
  - We usually work with students at Carnegie Mellon University (CMU), but students from other universities are also welcome. We accept both undergraduate and graduate students if they are motivated.
  - We emphasize the educational perspectives for speech processing, especially for students who are new to speech research. We guide students in understanding speech research background, required programming skills, knowledge of the cluster, and use of speech and audio toolkits. Students can also conduct research under our supervision. 
  - It usually takes a few months or even longer for students to obtain sufficient research skills before starting serious research activities. We believe this process is necessary and is essential for new researchers. If you want to publish a paper as soon as possible, our lab is not the best option for you, unfortunately. We recommend you contact the other faculties.

- Students who are interested in these opportunities should fill out **[this form](https://docs.google.com/forms/d/1AE-MMtqXpdPG07U6nnNfp9N2abJrI54XeVIshkyrwng/)**
  - If you fail to do so, we regard that you do not thoroughly investigate our lab's activities on this webpage, and unfortunately, we may not respond to your application.
  - The form will request your CV. Note that your CV will be shared with other lab members (but we do not distribute it outside).
  - If we find a good match between your background and our expertise, we will connect you with our lab members and arrange an interview.
- Please be prepared to present your past research clearly during the interview. A short slide presentation is very appreciated but not mandatory.
- Please refer to the [FAQ](#faq) to learn more about the interview and admission process. 
{: .pos-steps}

### Visiting Positions
{: #visiting}

- Please email your CV to shinjiw@ieee.org with the subject **"WAVLab visitor applications"**.
- If you do not put it in the subject, we regard that you do not thoroughly investigate our lab's activities on this webpage, and unfortunately, we may not respond to this email.
- Note that your CV will be shared with other lab members (but we do not distribute it outside).
- We will not have funding support for the visitor position, basically. So, therefore, we will only accept self-funded researchers.
- Please refer to the [FAQ](#faq) to learn more about the interview and admission process. 
{: .pos-steps}

### FAQ
{: #faq}

<div class="pos-faq" markdown="1">

{% details Do you have a Ph.D. opening? %}
Yes, we'll always have at least one Ph.D. position per year.
{% enddetails %}

{% details Who will I meet with during my interview? %}
The interview is of 2 stages

- A preliminary interview with Ph.D. students
- Interview with Prof. Shinji
{% enddetails %}

{% details What is the structure of the preliminary interview? %}
The structure of the interview is as follows-

- Basic Introduction of yourself as well as the interviewee (5 minutes)
- Discussion of research experience of the interviewee (20 minutes)
- General Questions (10 minutes)
- Quiz (10 minutes) -> Either about Neural networks or Language Model fundamentals
- Interviewee asks questions about lab (5 minutes)
{% enddetails %}

{% details What are interviews with Shinji like? %}
The structure of the interview is as follows-

- Introduction (5 minutes)
- General Questions (20 minutes)
- Interviewee asks questions about lab (5 minutes)
{% enddetails %}

{% details What can I expect following my interview? What are my chances for being accepted? %}
After we finish the interviews, The committee combines the information from the interviews to form a complete picture of the applicants. We consider the overall quality, as well as fit with our lab and the research diversity of the lab. We also consider applications from students who have previously not worked in speech processing. This process takes a few weeks, after which we notify students if they have been accepted, waitlisted, or rejected. Additionally, not all offers are sent at the same time. If someone else receives an offer and you haven’t heard yet, don’t be discouraged!
{% enddetails %}

{% details What should I do following my interviews? %}
Keep us informed of your status. If you are considering offers from other labs or have any deadlines specific to your program, please let us know. We try to move quickly, but we don’t want to lose a candidate who thinks that they won’t get in because they haven’t heard back yet.
{% enddetails %}

{% details What are potential projects? %}
We work on almost every aspect of speech processing, from frontends like speech enhancement to speech recognition and text to speech, as well as downstream tasks like speech translation and spoken language understanding. The research projects assigned to you depend on your interest and are decided after you are accepted into our lab.
{% enddetails %}

</div>

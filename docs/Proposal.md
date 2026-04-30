# Contents {#contents .TOC-Heading .unnumbered}

[1. Chapter One: Introduction.
[3](#chapter-one-introduction.)](#chapter-one-introduction.)

[1.0 Brief Introduction [3](#brief-introduction)](#brief-introduction)

[1.1 Background to the Study
[3](#background-to-the-study)](#background-to-the-study)

[1.2 Problem Statement [4](#problem-statement)](#problem-statement)

[1.3 Research Objectives
[5](#research-objectives)](#research-objectives)

[1.3.1 General Objective [5](#general-objective)](#general-objective)

[1.3.2 Specific Objectives
[5](#specific-objectives)](#specific-objectives)

[1.4 Research Questions.
[5](#research-questions.)](#research-questions.)

[1.5 Scope of the Study.
[6](#scope-of-the-study.)](#scope-of-the-study.)

[1.5.1 Geographical Scope [6](#geographical-scope)](#geographical-scope)

[1.5.2 Technical Scope [6](#technical-scope)](#technical-scope)

[1.5.3 Content Scope [7](#content-scope)](#content-scope)

[1.5.4 User Scope [7](#user-scope)](#user-scope)

[1.5.5 Limitations [8](#limitations)](#limitations)

[1.6 Justification [8](#justification)](#justification)

[1.6.1 Inadequacy of Existing Solutions
[8](#inadequacy-of-existing-solutions)](#inadequacy-of-existing-solutions)

[1.6.2 Availability of Foundational Technology
[9](#availability-of-foundational-technology)](#availability-of-foundational-technology)

[1.6.3 Supportive Policy Environment
[9](#supportive-policy-environment)](#supportive-policy-environment)

[1.6.4 Enabling Infrastructure.
[9](#enabling-infrastructure.)](#enabling-infrastructure.)

[1.6.5 Cost of Inaction [9](#cost-of-inaction)](#cost-of-inaction)

[1.7 Research Significance
[10](#research-significance)](#research-significance)

[1.7.1 To Visually Impaired Students
[10](#to-visually-impaired-students)](#to-visually-impaired-students)

[1.7.2 To Teachers [10](#to-teachers)](#to-teachers)

[1.7.3 To Schools [11](#to-schools)](#to-schools)

[1.7.4 To Government and Policymakers
[11](#to-government-and-policymakers)](#to-government-and-policymakers)

[1.7.5 To Researchers and Academia
[12](#to-researchers-and-academia)](#to-researchers-and-academia)

[1.7.6 To Society and National Development
[12](#to-society-and-national-development)](#to-society-and-national-development)

[1.7.7 To the Field of Assistive Technology
[12](#to-the-field-of-assistive-technology)](#to-the-field-of-assistive-technology)

[2. Chapter Two: Literature Review
[14](#chapter-two-literature-review)](#chapter-two-literature-review)

[2.1 Introduction [14](#introduction)](#introduction)

[2.2 Interactive Audio Learning Platforms for Visually Impaired Students
[14](#interactive-audio-learning-platforms-for-visually-impaired-students)](#interactive-audio-learning-platforms-for-visually-impaired-students)

[2.3 Case Studies [14](#case-studies)](#case-studies)

[2.4 Synthesis of the Literature
[16](#synthesis-of-the-literature)](#synthesis-of-the-literature)

[2.5 Conclusion [16](#conclusion)](#conclusion)

[3. Chapter Three: METHODOLOGY.
[18](#chapter-three-methodology.)](#chapter-three-methodology.)

[3.1 Requirement Gathering and Research Design.
[18](#requirement-gathering-and-research-design.)](#requirement-gathering-and-research-design.)

[3.2 System Design [18](#system-design)](#system-design)

[3.3 System Development [19](#system-development)](#system-development)

[3.4 System Testing and Validation
[20](#system-testing-and-validation)](#system-testing-and-validation)

[4 References [20](#references)](#references)

# Chapter One: Introduction.

## Brief Introduction

Visually impaired students in Uganda face a serious learning crisis.
Although some assistive tools exist, they only read text aloud and do
not allow students to actively learn, ask questions, receive feedback,
or track their progress. This project proposes an interactive
mobile-based audio learning platform that works offline on basic Android
phones. Teachers will upload lesson notes, and students will learn
through listening, answering questions, and getting immediate feedback,
supported by constrained AI that operates only on the uploaded content.

## Background to the Study

The persistent learning crisis for visually impaired students in Uganda
is underscored by the latest national data. In March 2025, UNEB
highlighted that only 10 out of 23 blind candidates passed their UACE
exams \[1\]. A year later, according to the 2025 UACE results released
on March 13, 2026, the number of Special Needs Education (SNE)
candidates rose to 540. Crucially, 112 of these 540 candidates (20.7%)
are visually impaired. While the national qualification rate for
university is 68.6%, only 96 SNE candidates total (including all
disability categories) achieved three principal passes. This indicates
that despite being a significant portion of the SNE population, visually
impaired students are disproportionately affected by the "rushed"
implementation of the new secondary curriculum, which experts at NUDIPU
state was designed without accessible digital interfaces in mind. The
data reflects a deeper systemic failure: the transition from passive
access to active learning. While a sighted student can read a textbook,
attempt practice questions, check answers, revise key points, and track
their progress, a visually impaired student using existing tools is
forced into a state of passive consumption. They cannot ask questions
when confused. They cannot practice what they learn. They receive no
feedback on whether they understand. They cannot revise efficiently
without re-listening to entire chapters. They have no way to know if
they are improving. In the context of Uganda\'s new competency-based
curriculum, which rewards critical thinking over rote memorization, this
lack of interaction is a decisive disadvantage. Several initiatives
exist but none solve this deeper problem due to fundamental
architectural limitations. Blind Assistant, developed in Uganda, reads
documents aloud and has trained 24 students at Sir Apollo Kaggwa
Secondary School \[2\]. However, it is limited by hardware-dependent
optical input---it only reads whatever is placed under a camera and does
not teach, question, or track progress. Yee FM provides over 150,000
audiobooks and eBooks but operates as a subscription-based "walled
garden" costing \$1.50 per week, offers no interaction, and lacks data
persistence for progress tracking \[3\]. The Blind Classroom in Malawi
uses voice interaction and an AI teacher, but requires custom hardware,
making it impossible to scale on the basic Android phones Ugandan
students already own \[4\]. Makerere University developed a Luganda
Neural Text-to-Speech system that works offline on basic phones. This
technology exists and is free \[5\]. But it remains a standalone
tool---the engine exists, but the chassis (the complete learning
platform) is missing.

The government has identified the lack of data on assistive technology
needs as a critical weakness. The Ministry of Health, with support from
**WHO**, is developing a rehabilitation database integrated into the
national **District Health Information Software version 2** (DHIS2)
platform \[6\]. Simultaneously, the Uganda Communications Commission has
profiled over 150,000 Persons with Disabilities through its ICT4PWDs
program \[7\]. However, these systems track needs without delivering
learning.

What is missing is not another tool that reads aloud. What is missing is
a platform that teaches. A platform where teachers upload their notes,
and students interact with content through listening, questions,
feedback, and progress tracking. A platform that works on the basic
phones students already have, offline-first and free of charge.

Unlike general-purpose AI chatbots that risk \"hallucinations\" or
require constant internet connectivity, this project proposes a
content-bound AI architecture inspired by Retrieval-Augmented Generation
(RAG) principles. By strictly constraining the AI\'s logic to the
teacher\'s uploaded text, the system ensures that generated questions
and summaries are accurate, curriculum-aligned, and capable of running
on low-resource, offline devices. This deterministic approach guarantees
that the AI serves as a reliable teaching assistant rather than an
unpredictable black box. This project fills that gap.

## Problem Statement

Despite the availability of screen readers and document-to-speech
applications, visually impaired students in Uganda remain passive
consumers rather than active learners. Existing assistive
technologies---including Blind Assistant, Yee FM, and JAWS---provide
auditory access to text but lack the pedagogical features necessary for
independent learning, questioning, practice, feedback, and progress
tracking. This pedagogical gap is particularly damaging under Uganda's
new competency-based curriculum, which requires active engagement and
critical thinking. This project will address this gap by developing an
offline-first, interactive audio learning platform for basic Android
phones. Teachers will upload lesson notes, and a content-bound AI engine
will generate curriculum-aligned questions, summaries, and feedback
strictly from that uploaded content, enabling visually impaired students
to learn independently regardless of internet connectivity.

## Research Objectives

### General Objective

To develop an offline-first, interactive audio learning platform that
enables visually impaired students in Uganda to learn independently on
basic Android phones by transforming teacher-uploaded notes into
structured, interactive audio lessons with automated questioning and
feedback.

### Specific Objectives

i)  To conduct a comprehensive requirements analysis by examining
    existing assistive technologies and gathering input from visually
    impaired students, teachers, and special needs education experts in
    Uganda.

ii) To design a scalable system architecture for an offline-first
    Android application that supports teacher note upload,
    text-to-speech conversion, interactive questioning, and local
    progress tracking.

iii) To implement a functional prototype incorporating core features:
     multi-format note processing (.txt, .docx, .pdf), text-to-speech
     playback with gesture-based controls, interactive questions, and
     local progress persistence.

iv) To develop and integrate a content-bound AI module that processes
    uploaded lesson notes during internet connectivity to generate
    curriculum-aligned questions, summaries, and feedback, which are
    then stored locally for completely offline student access.

v)  To evaluate the prototype through pilot testing in Ugandan schools,
    assessing usability, learning outcomes, and user satisfaction using
    mixed-methods analysis.

## Research Questions.

i)  What are the specific learning challenges faced by visually impaired
    students in Ugandan schools when using existing assistive
    technologies?

ii) What functional requirements and accessibility features do visually
    impaired students, teachers, and special needs experts identify as
    essential for an interactive audio learning platform?

iii) What system architecture best supports an offline-first Android
     application that enables teacher note upload, text-to-speech
     conversion, interactive questioning, and local progress tracking?

iv) How can multi-format educational notes (.txt, .docx, .pdf) be
    effectively processed, structured into learning units, and delivered
    through an accessible audio interface on basic Android devices?

v)  What is a feasible technical approach for implementing a
    content-bound AI module that generates curriculum-aligned questions,
    summaries, and feedback from uploaded lesson notes, balancing
    processing requirements with offline accessibility?

vi) To what extent does the proposed platform improve learning
    independence, comprehension, and engagement among visually impaired
    students during pilot testing?

vii) How do visually impaired students and teachers perceive the
     usability, usefulness, and overall satisfaction of the platform in
     real-world educational settings?

## Scope of­ the Study.

### Geographical Scope

The study will be conducted in selected Ugandan schools with established
programs for visually impaired learners. These include Sir Apollo Kaggwa
Secondary School in Mukono, where the Blind Assistant application has
been deployed and 24 students have received training, and Gulu Primary
School in northern Uganda, which reportedly serves 55 blind pupils
sharing only 8 Braille machines. These institutions provide direct
access to the target user population and represent both central and
regional educational contexts, enabling findings that are relevant
across different geographic and resource settings.

### Technical Scope

The project will deliver an Android-based mobile application designed
for offline-first functionality on basic smartphones. Core technical
features include:

  ------------------------------------------------------------------------------
  **Feature**          **Implementation Approach**
  -------------------- ---------------------------------------------------------
  **Note Upload**      Support for .txt, .docx, and text-based .pdf files

  **Text-to-Speech**   Android native TTS engine.

  **User Interaction** Simple gesture-based controls: tap (continue), double-tap
                       (repeat), swipe (next/previous)

  **Progress           Local storage using Room database; cloud sync when
  Tracking**           internet available

  **AI Module**        Content-bound processing during internet sessions to
                       generate questions, summaries, and feedback from uploaded
                       notes

  **Backend**          Python FastAPI with PostgreSQL for user management, note
                       storage, and anonymized analytics
  ------------------------------------------------------------------------------

The application will be developed using Kotlin in Android Studio,
targeting Android 8.0 (API level 26) and above to ensure compatibility
with the majority of basic smartphones in Uganda.

### Content Scope

The platform will support the Ugandan national curriculum across all
subjects and grade levels where teachers upload notes. The AI component
will be strictly constrained to operate only on the text contained
within uploaded lesson materials, ensuring that all generated questions,
summaries, and feedback are curriculum-aligned and content-reliable. No
external knowledge sources or open-domain AI models will be used,
guaranteeing that the platform\'s output remains predictable and
educationally appropriate.

### User Scope

The platform serves two primary user categories:

i)  **Primary Users:** Visually impaired students in Ugandan primary and
    secondary schools, including:

-   Totally blind students who require complete audio-based interaction

-   Low-vision students who may benefit from audio supplementation and
    adjustable text display

ii) **Secondary Users:** Teachers and special needs educators who will:

-   Upload and organize lesson notes by subject and topic

-   Monitor student progress through basic analytics

-   Provide feedback for platform improvement

The pilot validation phase will involve approximately 30-50 students and
5-10 teachers across 2-3 schools, providing sufficient data for
usability and learning outcome assessment.

### Limitations

The following aspects fall outside the scope of this study:

-   Development of iOS or web-based versions (Android-only for this
    phase)

-   Real-time voice recognition for student responses (gesture-based
    interaction prioritized for reliability)

-   Support for scanned image-based PDFs (only text-based PDFs will be
    processed)

-   Creation of original curriculum content (platform relies on
    teacher-uploaded notes)

-   Long-term deployment and maintenance beyond the pilot phase.

##  Justification

This project is necessary for four interconnected reasons: the
inadequacy of existing solutions, the availability of foundational
technology, the emergence of a supportive policy environment, and the
existence of enabling infrastructure. Each is examined below.

### Inadequacy of Existing Solutions

Current assistive technologies available in Uganda address access but
not learning. Screen readers such as JAWS (\$1,000+) and NVDA (free but
Windows-dependent) provide auditory access to on-screen text but offer
no pedagogical features \[8\]. Applications like Blind Assistant read
documents placed under a camera but cannot teach, question, or track
progress. Subscription-based platforms like Yee FM provide extensive
audiobook libraries but lack interaction and exclude students who cannot
afford the \$1.50 weekly fee. The consequences are evident in
examination outcomes: only 10 out of 23 visually impaired candidates
passed the 2025 UACE examinations , and 112 visually impaired candidates
in the 2026 UACE results were left behind by a curriculum designed
without accessible digital interfaces \[1\]. These outcomes confirm that
access alone does not produce learning.

### Availability of Foundational Technology

The core technology required for an interactive audio learning platform
already exists and is freely available in Uganda.  Android\'s native
Text-to-Speech engine provides additional language support. What remains
missing is not the underlying technology but the integrative
platform---the \"chassis\" that assembles these components into a
complete learning experience with teacher upload, interactive
questioning, feedback, and progress tracking. This project fills that
gap by building on existing local innovation rather than starting from
scratch.

### Supportive Policy Environment

The legal and policy landscape is increasingly favorable to assistive
technology deployment. The Copyright Amendment Bill, which had its first
reading in Parliament in May 2025, will permit the creation of
accessible format copies without seeking publisher permission, removing
a key legal barrier to textbook conversion. Simultaneously, government
data systems are being developed: the Ministry of Health, with WHO
support, is integrating a rehabilitation module into the national DHIS2
platform, and the Uganda Communications Commission has profiled over
150,000 Persons with Disabilities through its ICT4PWDs program. However,
these systems track needs without delivering learning. This platform can
complement them by providing the educational content delivery they lack,
and can feed ground-level data back into these national systems.

### Enabling Infrastructure.

The hardware necessary for deployment is already in the hands of
teachers and students. Teachers in Ugandan schools increasingly own
basic smartphones capable of running Android applications. Research at
Kyambogo University confirms that some visually impaired students
already use personal smartphones for academic purposes. The platform is
designed for offline-first operation, eliminating reliance on unstable
internet connectivity in rural areas and reducing battery consumption.
No new hardware purchases are required, making the solution scalable and
sustainable.

### Cost of Inaction

Without this project, visually impaired students will continue to be
passive listeners rather than active learners. The pedagogical gap will
persist, and the cycle of poor examination performance documented in the
2025 and 2026 UACE results will continue \[1\]. As Uganda implements its
new competency-based curriculum---which demands critical thinking,
practice, and active engagement---visually impaired students will fall
further behind their sighted peers, widening existing educational
inequalities. This project represents an opportunity to intervene before
that gap becomes insurmountable.

##  Research Significance

This project will deliver value across multiple stakeholder groups, from
individual learners to national policymakers. The significance is
examined below by stakeholder category.

### To Visually Impaired Students

Visually impaired students will gain the capacity for independent,
active learning. Unlike current solutions that reduce them to passive
listeners, the platform enables:

-   **Self-paced learning:** Students can repeat difficult sections
    without waiting for assistance.

-   **Immediate feedback:** Correct/incorrect responses provide instant
    reinforcement.

-   **Progress visibility:** Students can track their own learning
    journey.

-   **Active engagement:** Answering questions transforms consumption
    into participation.

-   **Offline access:** No dependency on internet connectivity or
    sighted assistance.

This shift from passive consumption to active participation addresses
the core pedagogical gap identified in the problem statement.

### To Teachers

Teachers will gain a practical tool that integrates into their existing
workflow without requiring specialized training or new hardware. The
platform enables:

-   **Reuse of existing materials:** Teachers can upload notes they
    already have, without reformatting.

-   **One-time upload, multiple access:** A single upload serves all
    visually impaired students indefinitely.

-   **No technical expertise required:** Simple upload interface
    designed for basic smartphone users.

-   **Progress visibility:** Basic analytics show which students are
    engaging with which content.

-   **Curriculum alignment:** Teachers organize content by subject and
    topic, maintaining pedagogical structure.

### To Schools

Schools serving visually impaired students will gain an affordable,
scalable solution that addresses a persistent resource constraint. The
platform offers:

-   **Cost elimination:** Free application compared to JAWS (\$1,000+)
    and subscription services (\$1.50/week).

-   **Hardware leverage:** Works on basic Android phones already in
    teachers\' possession.

-   **No infrastructure investment:** Offline functionality eliminates
    need for reliable internet.

-   **Equitable access:** All visually impaired students in a school can
    access the same content simultaneously, unlike Braille machines
    where 55 students share only 8 units.

-   **Scalability:** Once uploaded, content serves all students across
    all classes.

### To Government and Policymakers

The platform addresses the government\'s explicitly identified weakness:
the lack of reliable, granular data on assistive technology needs. It
will:

-   **Complement existing systems:** Feed ground-level data into the
    Ministry of Health\'s DHIS2 Rehabilitation Module and the UCC
    National Disability Digital Observatory.

-   **Inform resource allocation:** Provide district-level data on which
    schools need what assistive technology.

-   **Enable evidence-based policy:** Generate anonymized analytics on
    content access patterns, learning progress, and device usage.

-   **Support curriculum implementation:** Help the Ministry of
    Education understand how visually impaired students interact with
    the new competency-based curriculum.

###  To Researchers and Academia­­­

This project contributes to multiple academic domains:

-   **Assistive technology in low-resource settings:** Demonstrates an
    offline-first, phone-based approach scalable across Sub-Saharan
    Africa.

-   **Constrained AI in education:** Provides a case study in
    content-bound AI that avoids the risks of open-domain models.

-   **Human-computer interaction:** Advances knowledge on accessible
    design patterns for visually impaired users in African contexts.

-   **Software engineering:** Documents a replicable architecture for
    offline-first educational applications.

-   **Special needs education:** Generates empirical data on how
    interactive audio affects learning outcomes.

###  To Society and National Development

Beyond individual stakeholders, the project contributes to broader
societal goals:

-   **Inclusive education:** Aligns with Uganda\'s commitments under the
    Marrakesh Treaty (ratified 2018) and the UN Convention on the Rights
    of Persons with Disabilities.

-   **Sustainable Development Goals:** Contributes to SDG 4 (Quality
    Education) and SDG 10 (Reduced Inequalities).

-   **Human capital development:** Enables visually impaired students to
    complete education and contribute to the workforce.

-   **Digital equity:** Demonstrates that inclusive technology can be
    deployed without requiring expensive infrastructure.

###  To the Field of Assistive Technology

This project will produce a reusable framework for offline-first,
interactive audio learning platforms that can be adapted to other
contexts, languages, and disability categories. The technical
approach---combining teacher-uploaded content, text-to-speech engines,
constrained AI for question generation, and local progress
tracking---offers a replicable model for low-resource educational
settings globally.

#  Chapter Two: Literature Review

## Introduction

This chapter reviews existing literature on assistive technologies and
interactive audio learning platforms for visually impaired students. It
examines current tools available in Uganda and the region, identifies
their strengths and limitations, and highlights the specific pedagogical
gap that the proposed interactive mobile-based audio learning platform
aims to address.

## Interactive Audio Learning Platforms for Visually Impaired Students

> Interactive audio learning platforms convert educational content into
> spoken audio and allow students to actively engage with the material
> through questions, feedback, and progress tracking. Unlike basic
> screen readers that only read text aloud, these platforms aim to
> support active learning.
>
> In Uganda, most existing solutions focus on access rather than
> interaction. They provide text-to-speech but lack features such as
> practice questions, immediate feedback, or progress monitoring. This
> creates a significant pedagogical gap, especially under the new
> competency-based curriculum that requires critical thinking and active
> participation \[7\]. While some tools support local languages like
> Luganda, they remain limited in scope and do not enable truly
> independent learning for visually impaired students.

## Case Studies

i.  **Case Study 1: Blind Assistant (Uganda)**. Blind Assistant is a
    locally developed mobile application that uses a smartphone camera
    to scan printed documents and reads them aloud using text-to-speech
    technology. It has been piloted at Sir Apollo Kaggwa Secondary
    School, where it trained 24 visually impaired students.

> Its main strength is providing access to printed materials. However,
> its key weakness is hardware dependency --- it can only read text
> placed directly under the camera. It does not allow teachers to upload
> lesson notes, generate practice questions, provide feedback, or track
> student progress. Students remain passive listeners and cannot learn
> independently \[2\].

ii. **Case Study 2: Yee FM (Uganda)**. Yee FM is an AI-powered platform
    that provides over 150,000 audiobooks and e-books to users across
    Uganda \[3\]. It delivers content through audio and has reached
    approximately 2,000 registered users.

> Its strength lies in the large collection of accessible audio content.
> However, it operates as a paid subscription service costing \$1.50 per
> week and offers no interactive features such as practice questions,
> feedback, or progress tracking. Users can only listen passively \[3\].

iii. **Case Study 3: JAWS Screen Reader.** JAWS (Job Access With Speech)
     is a widely used commercial screen reader developed by Freedom
     Scientific. It converts on-screen text into speech or Braille
     output and supports a wide range of applications, including
     educational documents and web content \[8\]. It is popular in
     educational settings for blind and low-vision students.

> Its strength is its advanced navigation and productivity features.
> However, it is expensive (over \$1,000 per license), requires a
> Windows computer, and provides only passive reading without
> interactive questioning, feedback, or progress tracking. It is not
> designed for offline mobile use on basic Android phones common among
> Ugandan students \[8\].

iv. **Case Study 4: Blind Classroom (Malawi)**. Blind Classroom is an
    AI-powered, voice-controlled learning system developed by Access
    Ability Africa in Malawi. It enables visually impaired learners to
    navigate content, ask questions, and receive real-time feedback from
    an AI teacher \[4\].

> Its strength is true interactivity and curriculum-aligned support.
> However, its major limitation is that it requires custom hardware,
> making it difficult and expensive to scale in Uganda where students
> rely on basic Android phones. It is not offline-first and is not
> tailored to the Ugandan curriculum \[4\].

**\
**

**Comparison Table**

  --------------------------------------------------------------------------------
  **Feature /          **Blind       **Yee   **JAWS**   **Blind       **Proposed
  Characteristic**     Assistant**   FM**               Classroom**   System**
  -------------------- ------------- ------- ---------- ------------- ------------
  Works on basic       Yes           Yes     No         No            Yes
  Android phones                                                      

  Teacher can upload   No            No      No         Limited       Yes
  lesson notes                                                        

  Generates practice   No            No      No         Yes           Yes
  questions                                                           

  Provides immediate   No            No      No         Yes           Yes
  feedback                                                            

  Tracks student       No            No      No         Yes           Yes
  progress                                                            

  Completely offline   Limited       No      No         No            Yes
  operation                                                           

  Free for students    Yes           No      No         No            Yes
  --------------------------------------------------------------------------------

## Synthesis of the Literature

The reviewed literature shows that existing assistive technologies in
Uganda and the region successfully provide audio access to content but
fail to support active learning. Tools such as Blind Assistant, Yee FM,
JAWS, and Blind Classroom address the problem of reading or basic
interaction but leave students as passive consumers or require expensive
hardware \[2\], \[3\], \[8\], \[4\]. They lack the full set of
pedagogical features (questions, feedback, and progress tracking)
required by the new competency-based curriculum \[1\].

The literature also confirms that the necessary building blocks already
exist in Uganda: offline text-to-speech engines and widespread ownership
of basic Android phones. What is missing is an integrated platform that
combines these technologies into a complete, interactive learning
experience.

The proposed platform will fill this gap by allowing teachers to upload
notes, converting them into interactive audio lessons, generating
curriculum-aligned questions and feedback using constrained AI, and
enabling students to learn independently offline on the phones they
already own.

## Conclusion

Existing audio tools in Uganda and other regions have improved access
for visually impaired students but have not solved the deeper problem of
passive learning. The literature clearly reveals a consistent gap
between access and active engagement. The proposed interactive
mobile-based audio learning platform directly addresses this gap and
offers a practical, scalable solution tailored to Uganda's educational
context and the needs of visually impaired students.

# Chapter Three: METHODOLOGY.

This chapter outlines the specific steps that will be taken to achieve
the research objectives. The methodology follows a design science
research approach, which is suitable for developing and evaluating a
practical technological solution. Each specific objective is addressed
in the relevant subsection.

## Requirement Gathering and Research Design.

**Objective:** To conduct a comprehensive requirements analysis by
examining existing assistive technologies and gathering input from
visually impaired students, teachers, and special needs education
experts in Uganda.

Method:

A mixed-methods approach will be used.

-   First, a systematic literature review will be conducted on existing
    assistive technologies such as Blind Assistant, Yee FM, JAWS, and
    Blind Classroom.

-   Second, semi-structured interviews will be held with 10--15
    participants, including teachers at schools serving visually
    impaired students, representatives from the Uganda National
    Association of the Blind, and special needs education experts.

-   Third, questionnaires will be distributed to 30--50 visually
    impaired students and their teachers to collect quantitative data on
    current learning challenges, device ownership, internet access, and
    desired features.

The collected data will be analyzed using thematic analysis for
qualitative responses and descriptive statistics for quantitative data.
The output will be a detailed requirements specification document that
will guide the system design.

## System Design

**Objective:** To design a scalable system architecture for an
offline-first Android application that supports teacher note upload,
text-to-speech conversion, interactive questioning, and local progress
tracking.

**Method:** The system will be designed using Unified Modeling Language
(UML). The following diagrams will be developed:

-   Use Case Diagrams -- showing interactions between teachers
    (uploading notes) and students (listening and answering questions).

-   Sequence Diagrams -- illustrating the flow from note upload to text
    extraction, question generation, audio conversion, and student
    interaction.

-   Entity-Relationship Diagrams -- modelling the database structure for
    notes, questions, student progress, and user data.

Accessibility will be prioritized with linear navigation, large touch
targets, gesture-based controls, and screen reader compatibility. The AI
component will be designed as a content-bound module that processes only
teacher-uploaded notes. A low-fidelity prototype will be created and
reviewed with potential users before development begins.

## System Development

**Objective:** To implement a functional prototype incorporating core
features and to develop and integrate a content-bound AI module.

**Method:** The Android application will be developed using Kotlin in
Android Studio, targeting Android 8.0 (API level 26) and above for
compatibility with basic smartphones in Uganda. The following tools and
approaches will be used:

-   Note upload and processing: Support for .txt, .docx, and text-based
    .pdf files using Apache POI and PDFBox libraries.

-   Text-to-Speech: Android native TTS engine, supplemented by Makerere
    University's Luganda Neural TTS where applicable.

-   User interaction: Simple gesture controls (tap to continue,
    double-tap to repeat, swipe for next/previous).

-   Progress tracking: Local storage using Room database; cloud sync
    only when internet is available.

-   Content-bound AI: A lightweight rule-based NLP module will process
    uploaded notes during internet-connected sessions to generate
    practice questions, summaries, and feedback. All AI-generated
    content will be stored locally for completely offline use.

-   Backend: Python FastAPI with PostgreSQL for user management and
    anonymized analytics (deployed on a free cloud platform).

Development will follow Agile practices using Kanban boards to track
tasks in two-week sprints. Version control will be managed with Git.
Regular accessibility testing with TalkBack will be conducted throughout
development.

## System Testing and Validation

**Objective:** To evaluate the prototype through pilot testing in
Ugandan schools, assessing usability, learning outcomes, and user
satisfaction using mixed-methods analysis.

**Method:** Pilot testing will be conducted in two to three selected
schools with established programs for visually impaired learners (e.g.,
Sir Apollo Kaggwa Secondary School in Mukono and Gulu Primary School).
Approximately 30--50 visually impaired students and 5--10 teachers will
participate over a four-week period.

Testing will include:

-   Functional testing -- to verify note upload, audio playback,
    question generation, and offline operation.

-   Performance testing -- to ensure the application runs smoothly on
    basic Android phones.

-   User Acceptance Testing (UAT) -- involving students and teachers in
    real classroom settings.

Data will be collected through pre- and post-implementation
comprehension tests, System Usability Scale (SUS) questionnaires, task
completion rates, and focus group discussions. Quantitative data will be
analyzed using descriptive and inferential statistics (e.g., paired
t-tests for learning outcomes). Qualitative feedback will be analyzed
using thematic analysis. The findings will be documented in a pilot
evaluation report with recommendations for improvement.

# References

\[1\] 'Visually-impaired candidates fail exams', Monitor. Accessed: Mar.
26, 2026. \[Online\]. Available:
https://www.monitor.co.ug/uganda/news/national/visually-impaired-candidates-fail-exams-4965494

\[2\] AfricaNews, 'Uganda's blind assistant app: a step forward in
education', Africanews. Accessed: Mar. 26, 2026. \[Online\]. Available:
https://www.africanews.com/2024/08/05/ugandas-blind-assistant-app-a-step-forward-in-education/

\[3\] 'Yee FM Ai Virtual teacher Ebooks , research papers and Audiobooks
\| LinkedIn'. Accessed: Mar. 26, 2026. \[Online\]. Available:
https://ug.linkedin.com/company/yeefm

\[4\] 'Blind Classroom'. Accessed: Mar. 26, 2026. \[Online\]. Available:
https://blindclassroom.com/

\[5\] A. Isemaghendera, 'Translating Luganda Text into speech, An
Innovation at CEDAT', Makerere University News. Accessed: Mar. 27, 2026.
\[Online\]. Available:
https://news.mak.ac.ug/2024/02/translating-luganda-text-into-speech-an-innovation-at-cedat/

\[6\] M. Z. Hasan, G. Okello, W. D. Groote, A. Omaren, T. Adair, and A.
M. Bachani, 'Bridging the rehabilitation data gap in Uganda: a case
study exploring the implementation of the WHO Routine Health Information
System -- Rehabilitation module', *medRxiv*, p. 2025.02.13.25322214,
Sep. 2025, doi: 10.1101/2025.02.13.25322214.

\[7\] 'ICT for persons with disabilites'. Accessed: Mar. 27, 2026.
\[Online\]. Available: https://ict4personswithdisabilities.org/news/19

\[8\] 'JAWS Screen Reader Software \| Enabling Digital Accessibility for
Blind Users', Vispero. Accessed: Mar. 26, 2026. \[Online\]. Available:
https://vispero.com/jaws-screen-reader-software/

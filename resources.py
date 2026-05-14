"""
resources.py - Study Resource Recommender
Recommends YouTube channels and websites based on:
- Subject name (e.g., Physics, History, Maths)
- Exam type (e.g., UPSC, JEE, NEET, GATE, GRE, GMAT)

All data is curated and stored as a static dictionary (rule-based).
No API calls needed.
"""

# ─── RESOURCE DATABASE ────────────────────────────────────────────────────────
# Each entry has:
#   name        : Channel/site name
#   url         : Direct link
#   type        : 'youtube' or 'website'
#   description : Short description
#   tags        : List of subjects and exams this applies to
#   language    : 'English', 'Hindi', or 'Both'
#   free        : True/False

RESOURCES = [

    # ══════════════════════════════════════════════════════════
    # UPSC / IAS / CIVIL SERVICES
    # ══════════════════════════════════════════════════════════
    {
        "name": "StudyIQ IAS",
        "url": "https://www.youtube.com/@StudyIQEducation",
        "type": "youtube",
        "description": "Comprehensive coverage of all UPSC subjects — Polity, History, Economy, Current Affairs. Hindi & English.",
        "tags": ["upsc", "ias", "polity", "history", "economy", "geography", "current affairs", "general studies"],
        "language": "Both",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Unacademy UPSC",
        "url": "https://www.youtube.com/@UnacademyIAS",
        "type": "youtube",
        "description": "Top educators cover the entire UPSC syllabus with free live classes and recorded lectures.",
        "tags": ["upsc", "ias", "civil services", "general studies", "essay", "optional"],
        "language": "Both",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Drishti IAS",
        "url": "https://www.drishtiias.com/",
        "type": "website",
        "description": "Best UPSC prep website — daily current affairs, notes, practice questions, and mock tests.",
        "tags": ["upsc", "ias", "current affairs", "polity", "history", "geography", "economy"],
        "language": "Both",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "BYJU'S IAS",
        "url": "https://byjus.com/free-ias-prep/",
        "type": "website",
        "description": "Free IAS prep resources — NCERT summaries, previous year papers, and topic-wise notes.",
        "tags": ["upsc", "ias", "ncert", "general studies", "history", "polity"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "Insights IAS",
        "url": "https://www.insightsonindia.com/",
        "type": "website",
        "description": "Daily UPSC mains answer writing practice, current affairs summaries, and study plans.",
        "tags": ["upsc", "ias", "mains", "answer writing", "current affairs", "essay"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "Khan Sir Patna",
        "url": "https://www.youtube.com/@KhanGlobalStudies",
        "type": "youtube",
        "description": "Popular Hindi-medium channel for GK, Current Affairs, and reasoning for competitive exams.",
        "tags": ["upsc", "general knowledge", "current affairs", "ssc", "reasoning"],
        "language": "Hindi",
        "free": True,
        "icon": "🎓"
    },

    # ══════════════════════════════════════════════════════════
    # JEE (MAINS + ADVANCED)
    # ══════════════════════════════════════════════════════════
    {
        "name": "Physics Wallah (Alakh Pandey)",
        "url": "https://www.youtube.com/@PhysicsWallah",
        "type": "youtube",
        "description": "Best free JEE/NEET Physics & Chemistry channel. Simple, engaging, deeply conceptual.",
        "tags": ["jee", "neet", "physics", "chemistry", "class 11", "class 12"],
        "language": "Hindi",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Vedantu JEE",
        "url": "https://www.youtube.com/@VedantuJEE",
        "type": "youtube",
        "description": "Live JEE preparation classes covering Maths, Physics, Chemistry with doubt-clearing sessions.",
        "tags": ["jee", "maths", "physics", "chemistry", "jee mains", "jee advanced"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "3Blue1Brown",
        "url": "https://www.youtube.com/@3blue1brown",
        "type": "youtube",
        "description": "Visual mathematics — Calculus, Linear Algebra explained with stunning animations. Great for JEE Maths intuition.",
        "tags": ["jee", "gate", "gre", "maths", "calculus", "linear algebra", "mathematics"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "JEE Main & Advanced - Etoosindia",
        "url": "https://www.youtube.com/@etoosindia",
        "type": "youtube",
        "description": "Kota faculty lectures for JEE. Best for Maths and Physics advanced problems.",
        "tags": ["jee", "jee advanced", "maths", "physics"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Cuemath",
        "url": "https://www.cuemath.com/",
        "type": "website",
        "description": "Concept-based math learning with solved examples and practice problems for JEE level.",
        "tags": ["jee", "maths", "mathematics", "calculus", "algebra"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "JEE Main Official",
        "url": "https://jeemain.nta.nic.in/",
        "type": "website",
        "description": "Official NTA site for JEE Mains — mock tests, exam schedule, and previous year papers.",
        "tags": ["jee", "jee mains", "mock test", "previous papers"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },

    # ══════════════════════════════════════════════════════════
    # NEET
    # ══════════════════════════════════════════════════════════
    {
        "name": "Neela Bakore Tutorials",
        "url": "https://www.youtube.com/@NeelaBakoreTutorials",
        "type": "youtube",
        "description": "Biology concepts explained in depth — perfect for NEET Biology preparation.",
        "tags": ["neet", "biology", "botany", "zoology", "class 11", "class 12"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Aakash Institute NEET",
        "url": "https://www.youtube.com/@aakashinstitute",
        "type": "youtube",
        "description": "India's top NEET/JEE coaching — free lectures on Biology, Physics, Chemistry.",
        "tags": ["neet", "jee", "biology", "physics", "chemistry"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "NEET Prep by BYJU'S",
        "url": "https://byjus.com/neet/",
        "type": "website",
        "description": "Chapter-wise NEET notes, important questions, and previous year papers with solutions.",
        "tags": ["neet", "biology", "physics", "chemistry", "previous papers"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },

    # ══════════════════════════════════════════════════════════
    # GATE
    # ══════════════════════════════════════════════════════════
    {
        "name": "GATE Wallah (PW)",
        "url": "https://www.youtube.com/@GATEWallah",
        "type": "youtube",
        "description": "Complete GATE preparation — CS, ECE, ME, CE covered by experienced faculty.",
        "tags": ["gate", "computer science", "electronics", "mechanical", "civil", "engineering"],
        "language": "Hindi",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "NPTEL",
        "url": "https://nptel.ac.in/",
        "type": "website",
        "description": "IIT/IISc lecture series on all engineering subjects — the gold standard for GATE core subjects.",
        "tags": ["gate", "engineering", "computer science", "mathematics", "electronics", "mechanical"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "Gate Smashers",
        "url": "https://www.youtube.com/@GateSmashers",
        "type": "youtube",
        "description": "Computer Science GATE preparation — DBMS, OS, CN, Algorithms explained clearly.",
        "tags": ["gate", "computer science", "dbms", "operating systems", "networking", "algorithms"],
        "language": "Hindi",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Made Easy GATE",
        "url": "https://www.madeeasy.in/",
        "type": "website",
        "description": "India's leading GATE coaching — free study material, practice tests, and previous year solutions.",
        "tags": ["gate", "engineering", "mechanical", "civil", "electronics"],
        "language": "English",
        "free": False,
        "icon": "🌐"
    },

    # ══════════════════════════════════════════════════════════
    # GRE
    # ══════════════════════════════════════════════════════════
    {
        "name": "Magoosh GRE",
        "url": "https://www.youtube.com/@Magoosh",
        "type": "youtube",
        "description": "Free GRE prep — Vocabulary, Quant, Verbal Reasoning strategies and practice.",
        "tags": ["gre", "verbal", "quantitative", "vocabulary", "analytical writing", "gmat"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "GRE Prep Club",
        "url": "https://greprepclub.com/",
        "type": "website",
        "description": "Largest GRE community — thousands of practice questions, study plans, and forum discussions.",
        "tags": ["gre", "verbal", "quantitative", "practice questions"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "ETS GRE Official",
        "url": "https://www.ets.org/gre/test-takers/general-test/prepare.html",
        "type": "website",
        "description": "Official GRE prep materials — PowerPrep tests, sample questions from the exam makers.",
        "tags": ["gre", "official", "mock test", "verbal", "quantitative"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },

    # ══════════════════════════════════════════════════════════
    # GMAT
    # ══════════════════════════════════════════════════════════
    {
        "name": "GMAT Club",
        "url": "https://gmatclub.com/",
        "type": "website",
        "description": "The #1 GMAT community — thousands of practice questions, expert explanations, and study plans.",
        "tags": ["gmat", "quantitative", "verbal", "data insights", "problem solving"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "GMAT Prep by Veritas",
        "url": "https://www.youtube.com/@VeritasPrepGMAT",
        "type": "youtube",
        "description": "Expert GMAT strategies for Quant, Verbal, and Data Insights sections.",
        "tags": ["gmat", "quantitative", "verbal", "critical reasoning", "sentence correction"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },

    # ══════════════════════════════════════════════════════════
    # SUBJECT-SPECIFIC: MATHEMATICS
    # ══════════════════════════════════════════════════════════
    {
        "name": "Khan Academy",
        "url": "https://www.khanacademy.org/",
        "type": "website",
        "description": "World-class free education — Maths, Science, Computing from beginner to advanced level.",
        "tags": ["maths", "mathematics", "algebra", "calculus", "statistics", "jee", "gre", "gmat", "gate"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "Professor Leonard",
        "url": "https://www.youtube.com/@ProfessorLeonard",
        "type": "youtube",
        "description": "Full university-level Calculus, Statistics, and Algebra courses — extremely detailed.",
        "tags": ["maths", "calculus", "statistics", "algebra", "gre", "gate", "gmat"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },

    # ══════════════════════════════════════════════════════════
    # SUBJECT-SPECIFIC: SCIENCE
    # ══════════════════════════════════════════════════════════
    {
        "name": "CrashCourse",
        "url": "https://www.youtube.com/@crashcourse",
        "type": "youtube",
        "description": "Fast-paced, engaging video series covering Biology, Chemistry, Physics, History and more.",
        "tags": ["science", "biology", "chemistry", "physics", "history", "neet", "upsc"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "MIT OpenCourseWare",
        "url": "https://ocw.mit.edu/",
        "type": "website",
        "description": "Free MIT course materials — lecture notes, assignments, exams for all major subjects.",
        "tags": ["physics", "chemistry", "engineering", "maths", "computer science", "gate", "gre"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },

    # ══════════════════════════════════════════════════════════
    # SUBJECT-SPECIFIC: ENGLISH / VERBAL
    # ══════════════════════════════════════════════════════════
    {
        "name": "English with Lucy",
        "url": "https://www.youtube.com/@EnglishwithLucy",
        "type": "youtube",
        "description": "Vocabulary, grammar, and communication skills for competitive exam English sections.",
        "tags": ["english", "verbal", "vocabulary", "grammar", "gre", "gmat", "upsc"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Vocabulary.com",
        "url": "https://www.vocabulary.com/",
        "type": "website",
        "description": "Gamified vocabulary learning — great for GRE/GMAT word lists and UPSC English.",
        "tags": ["english", "vocabulary", "verbal", "gre", "gmat"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },

    # ══════════════════════════════════════════════════════════
    # SUBJECT-SPECIFIC: HISTORY / POLITY
    # ══════════════════════════════════════════════════════════
    {
        "name": "History of India - UPSC",
        "url": "https://www.youtube.com/@HistoryWithMohnish",
        "type": "youtube",
        "description": "Ancient, Medieval & Modern Indian History for UPSC — detailed and exam-focused.",
        "tags": ["history", "upsc", "ias", "ancient history", "modern history", "medieval"],
        "language": "Hindi",
        "free": True,
        "icon": "🎓"
    },
    {
        "name": "Laxmikanth Polity Notes",
        "url": "https://www.clearias.com/indian-polity/",
        "type": "website",
        "description": "Chapter-wise Indian Polity notes based on M. Laxmikanth — essential for UPSC.",
        "tags": ["polity", "upsc", "ias", "constitution", "governance"],
        "language": "English",
        "free": True,
        "icon": "🌐"
    },

    # ══════════════════════════════════════════════════════════
    # GENERAL COMPETITIVE EXAM / PRODUCTIVITY
    # ══════════════════════════════════════════════════════════
    {
        "name": "Testbook",
        "url": "https://testbook.com/",
        "type": "website",
        "description": "Mock tests for all major Indian exams — UPSC, SSC, GATE, NEET, JEE, RRB, Banking.",
        "tags": ["upsc", "jee", "neet", "gate", "ssc", "mock test", "practice", "general"],
        "language": "Both",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "Unacademy",
        "url": "https://unacademy.com/",
        "type": "website",
        "description": "India's largest learning platform — live & recorded courses for every competitive exam.",
        "tags": ["upsc", "jee", "neet", "gate", "gre", "gmat", "general"],
        "language": "Both",
        "free": True,
        "icon": "🌐"
    },
    {
        "name": "Ali Abdaal",
        "url": "https://www.youtube.com/@aliabdaal",
        "type": "youtube",
        "description": "Study techniques, productivity, and evidence-based learning strategies — great for any exam.",
        "tags": ["study tips", "productivity", "general", "exam strategy", "gre", "gmat"],
        "language": "English",
        "free": True,
        "icon": "🎓"
    },
]


# ─── RECOMMENDATION ENGINE ────────────────────────────────────────────────────

def normalize(text):
    """Lowercase and strip a string for comparison."""
    return text.lower().strip()


def get_recommendations(subject=None, exam_type=None, resource_type=None, top_n=8):
    """
    Get resource recommendations based on subject and/or exam type.

    Parameters:
        subject (str): Subject name (e.g., 'Physics', 'History')
        exam_type (str): Exam name (e.g., 'UPSC', 'JEE', 'GATE')
        resource_type (str): 'youtube', 'website', or None (both)
        top_n (int): Maximum results to return

    Returns:
        list of resource dicts, sorted by relevance score
    """
    if not subject and not exam_type:
        # Return general resources
        results = [r for r in RESOURCES if "general" in r["tags"]]
        return results[:top_n]

    # Build search terms
    search_terms = []
    if subject:
        search_terms.append(normalize(subject))
        # Also add individual words (e.g., "linear algebra" → ["linear", "algebra"])
        search_terms.extend(normalize(subject).split())
    if exam_type:
        search_terms.append(normalize(exam_type))

    # Score each resource
    scored_resources = []
    for resource in RESOURCES:
        score = 0
        resource_tags = [normalize(t) for t in resource["tags"]]

        for term in search_terms:
            for tag in resource_tags:
                if term in tag or tag in term:
                    # Exact match = 2 points, partial = 1 point
                    score += 2 if term == tag else 1

        # Bonus: free resources rank higher
        if resource["free"]:
            score += 0.5

        if score > 0:
            scored_resources.append((score, resource))

    # Sort by score descending
    scored_resources.sort(key=lambda x: x[0], reverse=True)

    # Filter by resource type if specified
    results = [r for _, r in scored_resources]
    if resource_type:
        results = [r for r in results if r["type"] == normalize(resource_type)]

    return results[:top_n]


def get_all_exam_types():
    """Return list of all supported exam types."""
    return ["UPSC / IAS", "JEE (Mains + Advanced)", "NEET", "GATE", "GRE", "GMAT"]


def get_all_subjects():
    """Return list of common subjects."""
    return [
        "Mathematics", "Physics", "Chemistry", "Biology",
        "History", "Geography", "Polity", "Economy",
        "English / Verbal", "Computer Science", "General Knowledge"
    ]


def get_resource_summary(resources):
    """
    Return a quick summary of recommended resources.
    """
    youtube_count = sum(1 for r in resources if r["type"] == "youtube")
    website_count = sum(1 for r in resources if r["type"] == "website")
    free_count = sum(1 for r in resources if r["free"])

    return {
        "total": len(resources),
        "youtube_channels": youtube_count,
        "websites": website_count,
        "free_resources": free_count
    }
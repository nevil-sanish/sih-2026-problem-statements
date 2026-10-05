# Smart India Hackathon (SIH) 2026 Problem Statements

This repository contains the scraped and structured problem statements for **Smart India Hackathon 2026** directly from [sih.gov.in/sih2026PS](https://sih.gov.in/sih2026PS).

## Available Files

- **[`all_problem_statements.md`](all_problem_statements.md)**: All 260 problem statements in a single comprehensive markdown file with a navigable Table of Contents and complete details.
- **[`SIH_2026_Problem_Statements.md`](SIH_2026_Problem_Statements.md)**: Identical single-file markdown reference.
- **[`all_problem_statements.json`](all_problem_statements.json)**: All 260 problem statements formatted as a clean structured JSON dataset.
- **[`problem_statements/`](problem_statements/)**: Directory containing individual `.md` files for each problem statement (`26001.md` through `26260.md`).
- **[`scrape_and_generate.py`](scrape_and_generate.py)**: Python automation script to fetch live data from SIH portal, clean formatting, and regenerate all files.

## Summary of Details Extracted

Each problem statement contains:
- **Problem Statement ID**
- **Problem Statement Title**
- **Description** (Background, Problem Description, Expected Solutions / Outcomes)
- **Organization**
- **Department**
- **Category** (Software / Hardware)
- **Theme** (e.g. Robotics and Drones, AI, Disaster Management, Clean & Green Technology, etc.)
- **Youtube Link**
- **Dataset Link**
- **Contact info**
- Additional metadata (Submission counts, deadlines)

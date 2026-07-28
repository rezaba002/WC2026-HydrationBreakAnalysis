# LinkedIn post — draft 3 (unpopular-opinion framing, tested without bias)

Target ~1,300–1,600 characters. Hook must stand alone in the first ~210.
Images: 1) stadium hydration-break photo  2) reports/figures/fig_case_studies.png

---

## POST BODY (copy from here)

Most of the hydration break debate came down to one argument: FIFA created them to sell advertising.

I had an unpopular opinion among my friends :)

I thought the breaks might actually be good for football.

I wasn't defending the ads. But there seemed to be footballing value nobody wanted to discuss: players could recover, and coaches got a rare chance to regroup and adjust.

So I spent the past week trying to prove myself wrong. That curiosity became a full data project on GitHub.

First, the money. Across the 104-match schedule the policy created 208 guaranteed mid-match slots; my dataset's 203 breaks produced about 9.7 hours of predictable stoppage. A new broadcast asset, and I can measure it. FIFA's intent, I can't.

Then came the football.

On coaches, I was half right. They didn't make more substitutions — 18.7%, slightly below the historical rate. They moved them: fewer in the three minutes before the stoppage, more in the three after. They waited, briefed the player at the cooler, sent him on at the restart.

On fresher players, I was wrong. Or rather, I can't show it. Substitutes at the break do run harder than the men they replace — but that's what substitutes do. Control for minutes played and the advantage disappears.

And the thing everyone else was sure about? The breaks didn't wreck the football either. Effect on shot balance: −0.073 shots, interval spanning zero. That famous drought is mostly the stopped clock — measure from the whistle and you spend three minutes counting players drinking water.

Even teams attacking before the break lost their advantage no faster than comparable teams nobody interrupted.

So my conclusion isn't that hydration breaks are good or bad. They changed how football was managed and broadcast far more clearly than they changed the next few minutes of shooting.

Full article, data and code:
https://github.com/rezaba002/WC2026-HydrationBreakAnalysis/blob/main/publication/ARTICLE.md

What's an unpopular opinion of yours that survived contact with the data?

#SportsAnalytics #FootballAnalytics #DataAnalysis

## END POST

---

## FIRST COMMENT (post immediately after)

Second image is my favourite thing in the project: six breaks picked by matrix, not by fame.

Top row, the feeling was real — Panama v England, Germany v Curaçao. Bottom row, the same
story was told about breaks where nothing measurable happened.

That gap is the whole finding. Pundits making specific claims were right about half the
time — but they were describing 4 of 48 randomly sampled breaks. Never a perception
problem. A sampling problem.

Two things I got wrong on the way:

• A strong directional result that survived every robustness check — until I tested the
control pool itself and found the bias was mine. Deleted, and documented.

• 46.8% of my "uninterrupted" control windows turned out to contain the actual break.
Fixing it shrank every sample and widened every interval.

Repo, frozen spec and dated amendment log:
https://github.com/rezaba002/WC2026-HydrationBreakAnalysis

PDF of the article:
https://github.com/rezaba002/WC2026-HydrationBreakAnalysis/blob/main/publication/WC2026_Hydration_Breaks_Article.pdf

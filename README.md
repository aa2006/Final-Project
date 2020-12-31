# Final Project
My final project for Harvard University's CS50.

# Live
Currently live at [https://encryption-project.herokuapp.com](https://encryption-project.herokuapp.com)

# About
My website is a prototype for a competitive encryption/decryption platform where users with administrator permissions (added by the root user) can add problems, specifying the prompt, number of points, correct answer, type of problem, and the title. All other users can then access the problem, and try to submit it. If the submission matches the answer given by the administrator, the user will get the problem's points. I played around with how to prevent users from getting points twice, so I ended up adding a seperate table on my database in order to track submissions. Users also have a profile, where they can update their bio, change their password.... On the leaderboard, you can see your rank in the world, and how much points you have, etc. You can also access other users' profiles from the leaderboard as well. There is an articles page, where users with administrator permissions can write articles, and a videos page where users with administrator permissions can upload videos.

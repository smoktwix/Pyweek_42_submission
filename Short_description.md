This is going to be a game developed using pygame.

It is a simulator-like game, where you click on an object repeatedly to gain points. Then you can spend those points on different things to help increase your clicking productivity. The game ends when time runs out or when the win variable is bought. You win or lose. It is similar to Cookie Clicker (https://orteil.dashnet.org/cookieclicker/)

In our game, a girl plays a cat-clicker simulator.  So the girl is clicking on the cat. She must buy the “Golden Kitty” before time runs out.

If the player wins: a "win cutscene" is shown (the cutscene shows that they get sucked into the game).

If the player loses: a "lose cutscene" is shown ( the cutscene shows they touch grass).

Here are the main components and functions of the game:
Points - The points earned so far. It is the Money used to buy Upgrades and Win the game.
The Cat - You have to Click the cat to get +1 Point (there is a Giant Cat in the Center of the screen)
Golden Kitty - Most Expensive, and the Main Goal.  Player's goal is to buy this and win. (Win Variable)
Timer - If Golden Kitty has not been bought once the timer is depleted, player gets a Game Over (Lose Variable). Total time of the game is 4 minutes.
—------------------------------------------
Upgrades available:
- Cat Petter - Purchased with 10 points.  Automatically Gives +1 Point per second (Can buy this at most 15 times in total. Each buy increases the price of next buy by 2)
- Litter Box - Purchased with 30 points. Increase the rate Cat Petters click by by 20% (Can buy this 5 times in total, Each buy increases the price of next buy of Litter Box by 10)
- Yarn Ball - Purchased with 80 points. Multiplies the points of Cat Petter by 2 each time (Can buy 6 of these. Each buy of this increase the Price by 80)
- Cat House - Purchased with 1000 points. Automatically Gives +100 Points per second (Can only get 1)
- Golden Kitty - Purchased with 5500 points.

When the play is on, there will be a static background image.

—------------------------------------------
Cutscenes:
Opening Cutscene
Win Cutscene
Game Over Cutscene

The title of the game is "Cat Clicker" (temporary, we may change the name later). When the game begins, a series of opening cutscenes are shown (open_cutscene_1.jpg, open_cutscene_2.jpg,..) The clicks to next one (may choose to go to a previous one).

If the player wins, they are shown win cutscenes (win_cutscene_1.jpg, win_cutscene_2.jpg, ...).The clicks to next one (may choose to go to a previous one).

If the player loses, they are shown lose cutscenes (lose_cutscene_1.jpg, lose_cutscene_2.jpg, ...).The clicks to next one (may choose to go to a previous one).

--

Picture Assets:
Opening, Win, and Lose Cutscenes
The Cat
Golden Kitty
Cat Petter
Litter Box
Yarn Ball
Cat House
Custom Mouse - we would like the "mouse" on the screen represented by a picture mouse
background image

Sound and Music for the game:

Concept Art:
See some concept art in concept_art/. There are two images. In Concept.png, nothing has been bought yet.  In Concept_Bought.png, some objects have been bought. (Cat Petter and Litter Box)

Implementation details:
- Litter Box upgrades compound: each multiplies all Cat Petters' speed by 1.2.
- Yarn Ball upgrades double all Cat Petters' output per purchase. Neither boost affects manual clicks or Cat House.
- The four-minute timer starts after the opening cutscenes. Pausing or switching away from the window freezes both time and automatic income. Returning to the window requires an explicit resume.
- Golden Kitty must actually be purchased before the deadline; merely reaching 5500 points does not win.
- The temporary cutscenes are PNG files, with three frames per sequence, as listed in assets/manifest.json.
- All tunable game settings live in cat_clicker/config.py.

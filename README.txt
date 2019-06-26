Team "Better than nothing", reflecting our ambition of getting a positive score!

Eric Stansifer and Yen-Ling Kuo

** Approach

In our submitted solution files, we never used the rotate commands, due to
<s>lack of time</s> our innovative strategy to focus on the bigger gains to be
had from cloning early and often.

Our solving technique involved two phases: first, a single worker collects all
the clones and spawns them (with possible diversions to teleporter boosters
and spawn points en route), then second the workers spread out and greedily search
for nearby squares that need painting. The painting algorithm was designed so
that workers would try to paint squares from locations with a y-coordinate
congruent to 1 mod 3, which would help to minimize overlap, and encourage them
to sweep left and right. (This worked much better on the block chain than on the
main tasks.)

The interesting thing about our game simulation was that it permitted the workers
to be desynchronized from each other, so each worker could be in a different time
step. This required some bookkeeping to make sure that, for example, workers
wouldn't use a booster that was collected by a worker that was in a future time,
or teleport to a teleporter that wasn't placed yet.

The searching algorithm was biased towards unpainted squares which are more
peripheral. To determine this, first we calculated for each point x in the graph

    P(x) = max_y d(x, y)

where the maximum is taken over all other points. This can be done in linear time.
Then, when taking a step from x to y where x and y are adjacent squares, we
say that the distance is B if P(y) < P(x) and 1 otherwise. (We tried B = 5
and B = 8 for every problem and chose the one that gave the better result.) This
bias towards the periphery was only for deciding which squares to paint next;
an unbiased pathfinding algorithm was used for things like pathing to the nearest
clone booster.

If a worker got too close to another worker, it would find the unpainted square
that was farthest from all the other workers and go there (using teleporters if
helpful). Note that because of the desynchronized nature of the workers, other
workers would not see that worker when it is in transit, but rather it would seem
to instantly cross the map. In particular, this meant that when two workers met
only one of them would go away. This was most helpful when a bunch of workers would
be spawned in one location in a few turns.

Due to the desynchronized nature, sometimes workers would continue working after
the map was fully painted, so we would restart and replay their actions in
synchrony and truncate the commands as soon as the painting was done.

Teleporters were always placed immediately where the booster was picked up.

** Other thoughts

It seemed that most of the boosters were useful in so far as they could be used to
support cloning. Teleporters found en route to the cloning boosters / spawn points
allow the cloned workers to spread out faster to cover distant territory,
and speed and drill boosters seemed only worthwhile for the initial worker to
make its clones faster. We lost interest in manipulator attachments when we
discovered that the clones were not clones but actually new workers lacking
the attachments.

We got in on the lambda chain market early, at block 5, using a very direct
greedy search. Since it was not allowed to submit solutions to tasks that
we had created, it became clear that it was desirable to submit the easiest tasks
possible so that as many other teams would get nearly optimal times, and thus
the lambda coins would be spread out across more other teams rather than
concentrated in only the strongest. For this reason we decided to submit tasks
that were very open rectangles, with as few walls as possible, although we
saw that other teams had submitted even easier tasks than those.

At the given market rates, purchasing clones was overwhelmingly a better choice
than the other boosters for nearly every circumstance. We spent all our coins
to buy 199 clones, which we distributed across the 199 tasks for which they
provided the most proportional improvement in our time.

It would have been possible to make a submission with only a single solution in
it, and looked at the resulting score to determine what the then-best solution
to that problem was. This could be repeated every 10 minutes to get an idea
of what the problem-by-problem standings were, but we didn't get around to
trying out such a system because we had higher priorities. It would have been
nice if the organizers had reported the scores we get in each problem so that
there would not be an incentive to make dummy submissions every 10 minutes to
get this information.

** How to run

To work on the lambda chain:

    cd src
    python chain.py

This checks every 5 minutes for the most recent block, and if we have not
already submitted to it makes a submission.

To solve a specific task:

    cd src
    python solvers.py <task filename>

To take a the computed solutions for all tasks and choose which ones get to buy clones:

    cd src
    python make_submission.py

To create some summary data of all 300 tasks

    cd src
    python run.py > task_summary

To try out a bunch of different bias levels B and compare how well they do:

    cd src
    python sampler.py > sampler_out

Various files:
    
    src/wrap.py         Handler for running solvers on a group of tasks
    src/task.py         Data structure describing a task
    src/gamestate.py    Game engine, interface for acting on workers, and pathfinding
    src/compute_interior.py     Compute the map described by a list of points
    src/puzzle.py       Read puzzles and come up tasks that satisfy them
    src/plan.py         First edition task solver
    src/solve_mod3.py   Task solver
    src/solvers.py      Try out different solvers and choose the best one
    src/solver_util.py  Handle cloning and calculations of periphery

# Reflection

> **About this document**
>
> I am dyslexic, and writing long texts is hard for me. That's why this
> reflection is set up as an interview, with questions and answers.
>
> - **The questions** (in boxes like this one) were written by an AI assistant
>   (Claude Code), based on the assignment's requirements (VG2–VG4) and my
>   notes from the project.
> - **The answers** are mine. I wrote them myself, and the AI only corrected
>   spelling and grammar and made them easier to read, without adding any
>   ideas of its own.

## 1. Saving after every change

> Every method that changes the server list (`add_server()`,
> `remove_server()`, `check_server()` and `check_all_servers()` in
> `services/inventory_service.py`) saves the data file right away through
> `InventoryService._save()`. Why did you want the program to save straight
> away after every change?

For me, it's important to know that as soon as you type in data or change a
value, it is recorded and saved right away. The less time it takes for the
data to be saved, the lower the risk that it gets lost. This is why most
programs today update in real time: you can see what's happening right in the
UI, without having to press a button to save or store your settings. It's just
a selection or a toggle away.

> What other way could you have done it?

The other way is to keep the data in memory and only store it when a save is
triggered. That can have benefits when adding things in bulk, where you need
to make sure that all the data passes before it's added to the storage. For
the scale this project is meant for, saving instantly is the better option.
For flexibility, there might be a case for using instant saves in the menu,
and bulk adding with a single save from the CLI. But that is something that
would come out of an architectural discussion about how the tool is used.

> What is the downside of saving after every change?

As I touched on in the previous answer, saving instantly might not be the best
choice for a larger bulk operation. That means a lot of transactions to the
file or database, and it would be a better fit to add everything in bulk and
then save once.

> At first, `save()` was a public method that the callers had to remember to
> call. In a code review you questioned that, and it became the private
> `InventoryService._save()` (PR #8). What was wrong with it being public, and
> what got better?

Having `save()` as a public method relies on other developers knowing that a
save has to be triggered for the data to be stored. Hiding it and triggering
it inside the `InventoryService` makes sure that whoever uses that interface
doesn't need to know what happens behind closed doors, and can be sure that
it's taken care of for them.

> If the tool had 1 000 servers, or several people used it at the same time,
> what would you do differently?

In that scenario, I would lean more towards a proper database connection
instead of writing to and reading from a file. I would also add support for
bulk operations, so that a large number of servers could be saved, updated and
deleted at once, rather than one at a time.

## 2. Splitting the program into packages and classes

> The course uses plain functions in flat modules, but the code is split into
> the package `server_inventory/` with the folders `storage/`, `services/` and
> `ui/`, and uses classes such as `ServerRepository`, `InventoryService`,
> `ServerChecker` and `Menu`. Why did you choose to structure it this way?

I have several years of experience working as a software developer, and
building code in a structured way is second nature to me. I come from C# and
.NET, where object-oriented programming (OOP) is common practice. There,
splitting the code into separate projects, libraries and NuGet packages and
referencing them is what makes the code easier to read and maintain.

> What is the job of each folder?

I separated the code into folders (modules) by their logical function. The
`storage` module takes care of loading and storing the data, and handles any
problems with those operations. The `services` module is where the business
logic lives: validation and all the functions behind the menu and the CLI.
This way, important functions aren't tied to the UI or to loading and saving
the data. For the UI, I made sure that the code is easy and clean to use and
simple to call. Since the UI is mostly about the menu, it's better to have it
separated as well. Building it this way keeps the code clean, readable and
easy to maintain, without the parts being coupled together.

> Some parts are still plain functions, like `is_valid_environment()` in
> `services/inventory_service.py` and `print_server_table()` in
> `ui/display.py`. Why not make everything a class?

Since the course mainly focused on a function-driven program, I leaned more
into that than I normally would, since C# builds basically everything from
classes. Python doesn't really have that strict "everything is a class"
architecture, so it was also a way to learn to do things in another way. It
also made the code base smaller, since not everything had to be built on a
class, with all the plumbing that comes with that.

> Requirement G1 says that each server must be a dictionary. How did that fit
> with your OOP plan?

It's an interesting way to do it, since I'm used to building a class to
represent the entity and using the object's properties to hold the data. That
way, the entity could also handle its own validation and processing. But a
dict is a nice way to do it, since it basically replicates how a class stores
its data, but without the bloat that comes with a class. Instead, the business
layer handles the validation, so it was an interesting way to solve it.

> What is the downside of this structure for a small tool like this one?

I wouldn't say there is really a downside, since all projects have their own
quirks and things you need to be mindful of. But if I should mention one, it's
that it's easier to get sloppy with smaller projects, since it's "just a small
thing for now". Then it usually gets used more than expected and grows in an
unplanned way. So keeping the edge and building the code in a maintainable way
is an important skill to learn, even for smaller projects, since they usually
don't stay that way.

> Say you wanted to add something new later, like an `--add` flag for the
> command line or a web page. How does the structure help, or not?

Since all the logic lives in the services module, it wouldn't be too hard to
add another method to handle the new CLI command. Once that is wired up, it's
simple to also add it as a menu option, if that is a requirement too. But as
the features grow, so does the file. There might come a time when it needs to
be split into separate files, maybe with an orchestrator that points to the
specific methods in their own files, using the main file as the public
interface.

## 3. Exit codes for every kind of error

> Requirement G16 only asks for exit code `0` (all good) and `1` (a server is
> down or doesn't exist). The program instead gives every kind of error its
> own code: the `ExitCode` enum in `exit_status.py` has codes 2–7 for things
> like invalid arguments, a broken data file or a missing `ping`, and 130 for
> Ctrl+C. Why did you choose to do that?

That comes down to having had to deal with programs that are really bad at
giving feedback on what is wrong. To be able to troubleshoot, you need as much
and as precise information as you can get, so you can pinpoint the issue.
Having several error codes, and making sure to document them (which isn't
always the case either), is an important step for that. Since the program
could be used by others than me, those people would need to know where to
start looking, in the code base or in their own process.

> Who is helped by having different codes?

The first people to come in contact with a tool like this would be other
DevOps engineers who might want to add it to their process and pipeline.
Setting it up and ironing out issues will be the first thing on their list
when they add a new tool to the tool belt. The error codes give them a head
start when debugging, and when setting up fallback procedures to make sure
that everything runs smoothly while it's in use.

> Each error class in `errors.py` (for example `DataFileInvalidError` and
> `PingNotAvailableError`) knows its own exit code, so `main()` in `main.py`
> handles all of them in one `except InventoryError` block. Why is that better
> than checking each error type in `main.py`?

This is mostly tied to the concept of encapsulation, mostly used in OOP, where
a class is only concerned with itself, its own data and its own state. Having
the errors and their codes in one file makes them easier to find, add to or
update when needed. It also cuts down on the size of `main.py`, which keeps
the code cleaner and makes it easier to follow each operation.

> What is the downside? For example, the error classes now "know about" exit
> codes, which are really a command line thing.

That's true, the codes are mostly used when the tool is part of a command line
workflow. But even then, it's still more information kept in the same place,
and as I mentioned above, that makes it easier to maintain and to find the
information needed to fix issues that might come up. So it might be a bit
redundant when using the menu, but in this case I would rather give too much
information than too little.

> If this code became a library that other programs use, what would you
> change?

That is actually not something I have thought of. It could quite easily be
moved as it is into its own module, and a stricter and more detailed list of
codes could be added over time to cover more failure modes. But programs are
also often very unique in their nature and in how things are implemented,
which makes it hard to cover every base with an error code for everything. So
it would be a nice library to have for internal tooling in a company, but
outside of that it might get too bloated to actually be useful to anyone.
Small, niche libraries are often easier to use and less demanding on
resources.

## 4. Private methods by convention

> Python has no `private` keyword like C#. A name that starts with `_`, like
> `InventoryService._save()`, `ServerChecker._ping()` or
> `ReportExporter._build_report_filename()`, only tells other developers
> "don't use this from outside". Python doesn't stop them. Why did you mark
> methods as private with `_` anyway?

This is a habit from working in C# and .NET, where everything is public,
internal or private, since it's based on the principles of OOP. Making it
clear when a method is only used internally, rather than exposed to the rest
of the code base, makes it easier to follow the logical paths in the code.

> How did you decide what should be public and what should be private?

The principle is that a public method is exposed to the rest of the code, and
then handles the request internally. A similar analogy is a car: turning the
key to start it is quite easy, while looking at the actual engine is a lot
more complex to deal with.

> You also structured every class with `# region Public methods` and
> `# region Private methods` blocks. Why?

The simple answer is that it helps me structure the code in the IDE I'm
working in. I can fold regions of code together when I only need to work on
the public interface, or when I need to fix a bug that is internal to the file
itself. And since Python doesn't enforce public and private, the regions give
the code a clear structure that keeps it more maintainable.

> What is the downside of privacy that is only a convention?

The downside is that it can't be enforced. If someone wants to use one of the
private functions, they can, and there's no real way to stop it. But if this
project were built by a team, there would also be company policies for how to
work with the code base, usually set by the project architect or project
manager.

> If more people worked on the code, or it was used as a library, what would
> you do differently?

I think most of the project is covered by a kind of softly enforced structure,
where I would hope that most team members see and follow the conventions set
for this code base. But that only goes so far in terms of what the code itself
can do. The next step would be to also enforce it in code reviews and pull
requests, and even before that, to make sure new colleagues are onboarded into
the process of working with this code base.

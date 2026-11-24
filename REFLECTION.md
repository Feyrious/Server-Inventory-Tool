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

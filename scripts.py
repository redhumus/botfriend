from nose.tools import set_trace
from argparse import ArgumentParser
from config import Configuration

class Script(object):
    pass

class BotScript(Script):
    """A script that operates on one or more bots."""

    @classmethod
    def parser(cls):
        parser = ArgumentParser()
        parser.add_argument(
            '--config',
            help="Directory containing the botfriend database.",
            required=True,
        )
        parser.add_argument(
            '--bot', 
            help='Operate on this bot.',
            nargs='*'
        )
        return parser
    
    def __init__(self):
        parser = self.parser()
        self.args = parser.parse_args()
        self.config = Configuration.from_directory(self.args.config)

    def run(self):
        for model in self.config.bots:
            if self.args.bot and not any(x in self.args.bot for x in (model.name, model.implementation.module_name)):
                # We're processing specific bots, and this one isn't
                # mentioned.
                continue
            self.process_bot(model)

    def process_bot(self, bot_model):
        raise NotImplementedError()


class PostScript(BotScript):
    """Create a new post for one or all bots."""

    @classmethod
    def parser(cls):
        parser = BotScript.parser()
        parser.add_argument(
            '--dry-run',
            help="Show what would be posted, but don't post it or commit to the database.",
            action='store_true'
        )
        return parser
    
    def process_bot(self, bot_model):
        post = bot_model.implementation.new_post()
        if self.args.dry_run:
            print bot_model.name
            print post.content
            print "-" * 80
            return
        for publication in post.publish():
            print publication.display()
            bot_model.schedule_next_post(self, post)
        self.config._db.commit()        
    


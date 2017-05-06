from errbot import BotPlugin, botcmd
import logging

#log = logging.getlogger(name='errbot.plugins.imdb')

try:
    from imdbpie import Imdb
except:
    log.error("please install 'imdbpie' python package")


class imdb(BotPlugin):

    def get_configuration_template(self):
        """ configuration entries """
        config = {
            'anonymize': False,
            'cache': False,
            'cache_dir': u'/tmp/imdbpiecache',
        }
        return config

    def _check_config(self, option):

        # if no config, return nothing
        if self.config is None:
            return None
        else:
            # now, let's validate the key
            if option in self.config:
                return self.config[option]
            else:
                return None

    def _connect(self):
        """ connection to imdb """

        anonymize = self._check_config('anonymize') or False
        cache = self._check_config('cache') or False
        cache_dir = self._check_config('cache_dir') or '/tmp/imdbpiecache'

        imdb = Imdb({
                    'anonymize': anonymize,
                    'cache': cache,
                    'cache_dir': cache_dir,
                    })

        return imdb

    def _parse_movie_results(self, results, more=""):
        response = []
        count = 1
        response.append('Results:\n')
        for result in results:
            # x. title (year) / <code>
            if more:
                imdb = self._connect()
                movie = imdb.get_title_by_id(result['imdb_id'])
                if len(movie.cast_summary)==0:
                    name=""
                else:
                    name=movie.cast_summary[0].name
                response.append('{0}. {1} - {4} ({2}/{3})\n'.format(
                count,
                result['title'],
                result['year'],
                movie.rating,
                name,
                ))
            else:
                response.append('{0}. {1} ({2}/{3})'.format(
                count,
                result['title'],
                result['year'],
                result['imdb_id'],
                ))
            count = count + 1
        logging.debug(response)
        return ''.join(response)

    @botcmd
    def imdbf(self, msg, args):
        ''' Search for movie titles
            Example:
            !imdbf The Dark Knight
        '''
        imdb = self._connect()
        results_to_return = 8

        results = imdb.search_for_title(args)
        results_total = len(results)

        if results_total == 0:
            self.send(msg.frm,
                      'No results for "{0}" found.'.format(args),
                      #message_type=msg.type,
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
            self.send(msg.frm,
                     'END'.format(''),
                     in_reply_to=msg,
                     groupchat_nick_reply=True)    
            return

        movies = self._parse_movie_results(results[:results_to_return],"full")
        logging.debug(movies)
        self.send(msg.frm,
                  '{0}'.format(movies),
                  in_reply_to=msg,
                  groupchat_nick_reply=True)    
        self.send(msg.frm,
                  'END'.format(''),
                  in_reply_to=msg,
                  groupchat_nick_reply=True)    

    @botcmd
    def imdb(self, msg, args):
        ''' Search for movie titles
            Example:
            !imdb The Dark Knight
        '''
        imdb = self._connect()
        results_to_return = 5

        results = imdb.search_for_title(args)
        results_total = len(results)

        if results_total == 0:
            self.send(msg.frm,
                      'No results for "{0}" found.'.format(args),
                      #message_type=msg.type,
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
            self.send(msg.frm,
                     'END'.format(''),
                     in_reply_to=msg,
                     groupchat_nick_reply=True)    
            return


        movies = self._parse_movie_results(results[:results_to_return])
        self.send(msg.frm,
                  '{0}'.format(movies),
                  #message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)
        self.send(msg.frm,
                  'END'.format(''),
                  in_reply_to=msg,
                  groupchat_nick_reply=True)    

    @botcmd
    def imdb_movie(self, msg, args):
        ''' Get movie details
            Example:
            !imdb movie tt0468569
        '''

        imdb = self._connect()
        movie_id = args

        try:
             imdb.title_exists(movie_id)
        except:    
            self.send(msg.frm,
                      'Movie id ({0}) not valid.'.format(movie_id),
                      #message_type=msg.type,
                      in_reply_to=msg,
                      groupchat_nick_reply=True)
            self.send(msg.frm,
                     'END'.format(''),
                     in_reply_to=msg,
                     groupchat_nick_reply=True)    
           return

        movie = imdb.get_title_by_id(movie_id)

        # Title (year), Plot: ..., Release: xxxx-xx-xx, imdb-url
        response = '{0} ({1}), Plot: {2} Released: {3}, {4}, {5}'.format(
            movie.title,
            movie.year,
            movie.plot_outline,
            movie.release_date,
            'http://www.imdb.com/title/{0}/'.format(movie.imdb_id),
            movie.rating,

        )

        self.send(msg.frm,
                  response,
                  #message_type=msg.type,
                  in_reply_to=msg,
                  groupchat_nick_reply=True)
        self.send(msg.frm,
                  'END'.format(''),
                  in_reply_to=msg,
                  groupchat_nick_reply=True)    


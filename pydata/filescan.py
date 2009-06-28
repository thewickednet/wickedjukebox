"""
File scanner - revision 3

This module provides the functionality to scan files in a directory. Each file
can be filtered through a filter-chain, and then each un-filtered file will be
run through a process-chain
"""

import logging
from os.path import join
LOG = logging.getLogger(__name__)

def processor_printout( root, filename ):
   """
   Simply prints out the filename
   """
   print "Processed: %r" % ( filename )

def filter_example( root, filename, char ):
   """
   Prints out some data and filers files containing the letter "char"
   """

   if filename.find( char ) > -1:
      LOG.debug( "filtering %r for %r" % (filename, char) )
      return True
   LOG.debug( "not filtering %r for %r" % (filename, char) )
   return False

def _sanity_check( thelist ):
   """
   Checks if filters or processors are passed correctly.

   @param thelist: The list of filters/processors
   @raises: ValueError on invalid entry
   """
   # sanity checks on the filter/processors elements
   if not thelist:
      return

   for element in thelist:
      if not hasattr( element, "__call__") and not hasattr( element, "index"):
         raise ValueError( "%r is not a valid filter/processor element. It must either be callable, or be a indexable object (f. ex. a list or tuple) containing a callable and a list of parameters" % element )
      elif hasattr( element, "index" ) and not hasattr( element[0], "__call__" ):
         raise ValueError( "%r is not a valid filter/processor element. The first element is not callable!" % element )
      elif hasattr( element, "index" ) and len(element) != 2:
         raise ValueError( "%r is not a valid filter/processor element. It does not contain exactly 2 elements (callable with arguments)" % element )
      elif hasattr( element, "index" ) and not hasattr( element[1], "index" ):
         raise ValueError( "%r is not a valid filter/processor element. Second element must be indexable!" % element )

def _ignore_file( filters, root, fname ):
   """
   Processes the filters
   @return: "True" if any filter returned "True", otherwise "False"
   """
   ignore_file = False
   if filters:
      for fltr in filters:
         if hasattr( fltr, "__call__" ):
            # filter is callable as itself. go ahead and call it
            if fltr( root, fname ):
               ignore_file = True
               break
         else:
            # (see sanity checks above) filter is a two-element indexable with a callable and parameters
            if fltr[0]( root, fname, *fltr[1] ):
               ignore_file = True
               break
   return ignore_file

def _run_process_chain(processors, root, fname):
   """
   Run the process chain on a filename
   """
   return_val = None
   if processors:
      for proc in processors:
         if hasattr( proc, "__call__" ):
            # processor is callable as itself. go ahead and call it
            callable = proc
         else:
            # (see sanity checks above) processor is a two-element indexable with a callable and parameters
            callable = proc[0]
            # ensure that the previous return_value is compatible with a parametrized processor
            if return_val and not hasattr( return_val, "index" ):
               raise ValueError("Processor %r is incompatible with the previous (non-indexable) return value %r!" % (callable, return_val) )

            # append the run-tie parameters to the return value
            if return_val and proc[1]:
               return_val.extend(proc[1])
            elif proc[1]:
               return_val = proc[1]

         if isinstance( return_val, tuple ) or isinstance( return_val, list ):
            return_val = callable( root, fname, *return_val )
         elif isinstance( return_val, dict ):
            return_val = callable( root, fname, **return_val )
         else:
            return_val = callable( root, fname )

def scan(root, filters = None, processors=None):
   """
   Scans files in a specific directory.

   @param root: The root directory to scan
   @param filters: A list of filter methods applied to each filename. The
                   methods should return a valid truth value. If the falue is
                   true, the filename is *ignored* (filtered). Note that each
                   filter is called for each file. If this list becomes long,
                   it will seriously slow down scanning!
                   The filters have the following signature:
                   filter_example( root, filename )
                   If one of the filters matches, the file is ignored. The
                   filters are evaluated in turn. As soon as one matches, the
                   file is considered as "ignored". To increase performance
                   when using many filters, it's wise to put the least
                   permissive filters on the beginning of the list.
                   If, the filter requires run-time parameters, add them as a
                   second element to the filter list element.

                   Example filter list:
                     [ filter_1,
                       filter_2,
                       (filter_3, (param1, param2))
                       ]

   @param processors: A process chain which is called evaluated for each valid
                   file in turn. Each callback (processor) method will have the
                   following signature::

                      processor_example( root_folder, filename )

                   Some major magic is possible here. If a callback returns a
                   list or tuple, these values are injected as positional
                   parameters to the following processor in the chain. If a
                   processor returns a dictionary, these values are injected as
                   keyword parameters.

                   This means that it would be clever to give the processors a
                   more generic signature::

                     processor_example( root_folder, filename, *args, **kwargs )

                   If, the processor requires run-time parameters, add them as a
                   second element to the processor list element.

                   Example processor list:
                     [ processor_1,
                       processor_2,
                       (processor_3, (param1, param2))
                       ]

                  WARNING:
                     processors which take run-time parameters, will only be
                     able to take positional arguments from the previous
                     processor.
                     run-time arguments will be *appended* to the call from the
                     previous processor!

                     If unsure, write a generic processor which will print the
                     passed arguments::

                        def processor_generic( *args, **kwargs ):
                           print "Positional args: ", repr(args)
                           print "Keyword args   : ", repr(kwargs)
   @return: Count of files processed
   """
   from os import walk

   _sanity_check( filters )
   _sanity_check( processors )

   count = 0
   for path, dirs, files in walk(root):

      for fname in files:
         if _ignore_file(filters, root, join(path, fname)):
            continue
         count += 1
         _run_process_chain(processors, root, join(path, fname))
   return count

if __name__ == "__main__":
   import sys
   logging.basicConfig(level=logging.DEBUG)
   scan( sys.argv[1], filters = None,
      processors = [
         processor_printout,
         ]
      )

- If a song was prefetched, exclude it from the new prefetch query. It has
  probably a high score and would very likely be prefetched again.
- Implement a file-based queuing (like the IPC) for easier testing
- Implement socket-based IPC for easier testing
- Review which progress bar libraries are available and modernise if needed
  (see "rich")
- Add "pusher" events back
- Review "queue" behaviour for "history" entries
- Ensure each datetime field has a timezone
- Ensure each foreign-key column has a proper type
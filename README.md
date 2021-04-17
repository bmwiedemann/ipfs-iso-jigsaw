We want to efficiently store iso images,
that change daily
but mostly contain the same rpms again
and we do want to re-use rpm CIDs
so we scan the .iso for rpm magic header bytes
and chunk accordingly


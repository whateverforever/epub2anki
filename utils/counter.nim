import algorithm
import sugar
import nimpy
import tables

type
    CountResult = tuple
        lemma: string
        count: int
        idxs: seq[int]

func countWithIndex(lemmas: seq[string]): seq[CountResult] {.exportpy.} =
    var res: Table[string, CountResult]

    for ilem, lem in lemmas:
        if not (lem in res):
            res[lem] = (lem, 0, @[])

        res[lem].count += 1
        res[lem].idxs.add(ilem)

    let resSeq = collect(newSeq):
        for key, val in res:
            val

    return resSeq.sorted(func (x,y:CountResult):int =
        cmp(y.count, x.count))

func removeDuplicates(wordList: seq[string]): seq[string] {.exportpy.} =
    var res: seq[string]

    for word in wordList:
        if not (word in res):
            res.add(word)
    
    return res
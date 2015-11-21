# pandoc-filters

A collection of my own pandoc filters for "minted", "plantuml", and so on

# PlantUML

For this filter, you need to have "plantuml" installed on your system and to accessible in you `$PATH`.

Generated graph will reside in `/tmp` directory.

This filter parse block code referenced as "plantuml":


    ```plantuml
    A -> B
    ```

You may use "caption" to build title.

# minted

Latex generation only. Special actions for Go.

This filter check code block to be injected as "minted" listing. It allow some nice features as:

- include file
- ommiting lines
- extract block of code delimited by comments

Example:

Generate minted block:

    ```go
    var a string
    ```

Generate minted block from a file:

    ```go include="path/to/file.go"
    ```

Extract block:

If you file describes:

```go
package main

import "fmt"

func main () {

    // START EXAMPLE
    fmt.Println("Document will only read this")
    // END EXAMPLE
}
```

This inclusion will only get the line in EXAMPLE BLOCK

    ```go include="path/to/file.go" block=EXAMPLE
    ```

To omit line, add "OMIT" in comment, example:

```go
func main() { // OMIT
    fmt.Println("This line appears, but not func() and brackets")
} // OMIT
```


It's recommanded to OMIT block definition to not see them in document:

```go
package main

import "fmt"

func main () {

    // START EXAMPLE OMIT
    fmt.Println("Document will only read this")
    // END EXAMPLE OMIT
}
```

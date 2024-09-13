import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import axios from "axios"
import { useEffect, useState } from "react"
import { EntityList } from "./content"
import { Button } from "./ui/button"


interface ContentProps {
    entityList: EntityList
    updateTable: (name: string) => void
}


function Filetable( { entityList, updateTable }: ContentProps ){

    return(
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[100px]"></TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>
                        <Button>Add</Button>
                    </TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                {
                    entityList.map(ent => (
                        <TableRow key={`${ent._id}`}>
                            <TableCell>
                                <Avatar>
                                    <AvatarImage src={`${ent.type}.svg`} />
                                    <AvatarFallback>{ent.type}</AvatarFallback>
                                </Avatar>
                            </TableCell>
                            <TableCell>
                                <Button onClick={() => {if(ent.type !== 'file') updateTable(ent.path)}}>
                                    {ent.name}
                                </Button>
                            </TableCell>
                            <TableCell>11.09.2024</TableCell>
                            <TableCell>{ent.type}</TableCell>
                        </TableRow>
                    ))
                }
            </TableBody>
        </Table>
    )
}

export default Filetable
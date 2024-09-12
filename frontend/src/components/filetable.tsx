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


interface Entity {
    _id: string
    name: string
    type: string
    owner: string
    parent: string
    path: string
}

type EntityList = Entity[];


function Filetable(){
    const fetchFiles = (): EntityList => {
        let entityList: EntityList = []

        axios.get('https://127.0.0.1:8000/api/workspace//', {
            withCredentials: true,
        })
        .then(resp => {
            console.log('api/workspace//', resp);
            entityList = resp.data['entity_list'];
        })

        return entityList
    };

    const [tableBody, setTableBody] = useState([<></>]);

    useEffect(() => {
        const entityList: EntityList = fetchFiles();

        let tableElements = entityList.map(ent => (
            <TableRow key={`${ent._id}`}>
                <TableCell>
                    <Avatar>
                        <AvatarImage src={`${ent.type}.svg`} />
                        <AvatarFallback>{ent.type}</AvatarFallback>
                    </Avatar>
                </TableCell>
                <TableCell>{ent.name}</TableCell>
                <TableCell>11.09.2024</TableCell>
                <TableCell>{ent.type}</TableCell>
            </TableRow>
        ))

        setTableBody(tableElements)
    }, []);

    return(
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[100px]"></TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                </TableRow>
            </TableHeader>
            <TableBody>
                { tableBody }
            </TableBody>
        </Table>
    )
}

export default Filetable
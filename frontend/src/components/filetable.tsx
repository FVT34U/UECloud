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
import { useEffect } from "react"


function Filetable(){
    const fetchFiles = () => {
        axios.get('http://127.0.0.1:8000/api/workspace//', {
            withCredentials: true,
        })
        .then(resp => {
            console.log('api/workspace//', resp)
        })
    };

    useEffect(() => {
        fetchFiles()
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
            <TableRow>
                <TableCell>
                    <Avatar>
                        <AvatarImage src="workspace.svg" />
                        <AvatarFallback>WS</AvatarFallback>
                    </Avatar>
                </TableCell>
                <TableCell>adminsk</TableCell>
                <TableCell>11.09.2024</TableCell>
                <TableCell>workspace</TableCell>
            </TableRow>
        </TableBody>
    </Table>
    )
}

export default Filetable
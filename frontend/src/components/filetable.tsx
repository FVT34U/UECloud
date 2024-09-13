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


interface ContentProps {
    entityList: EntityList
}


function Filetable( { entityList }: ContentProps ){
    // const [localEntityList, setEntityList] = useState<EntityList>([]);

    // useEffect(() => {
    //     const fetchData = async () => {
    //         const data = entityList;
    //         setEntityList(data);
    //         console.log('useEffect', entityList);
    //     }

    //     fetchData();
    // }, []);

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
                {
                    entityList.map(ent => (
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
                }
            </TableBody>
        </Table>
    )
}

export default Filetable
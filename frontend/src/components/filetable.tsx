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
import { useEffect, useRef, useState } from "react"
import { EntityList } from "./content"
import { Button } from "./ui/button"


interface ContentProps {
    entityList: EntityList
    path: string
    updateTable: (name: string) => void
    downloadFile: (path: string, type: string) => void
    uploadFile: (file: File | undefined, path: string | undefined) => void
}


function getActions(type: string, downloadFile: (path: string, type: string) => void, path: string) {
    if (type === 'file') {
        return (
            <>
                <Button onClick={ () => {downloadFile(path, type)} }>Download</Button>
            </>
        )
    }
    return (<></>)
}


function Filetable( { entityList, path, updateTable, downloadFile, uploadFile }: ContentProps ){

    const nameForButton = () => {
        if (entityList.length === 0) {
            return 'Add'
        }
        else if (entityList[0].type !== 'workspace' && entityList[0].type !== 'project') {
            return 'Add new folder/file'
        }
        return `Add new ${entityList[0].type}`
    }

    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleButtonClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        uploadFile(file, `${path.split('/').slice(0, -1).join('/')}/${file?.name}`)
    };

    return(
        <Table>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[100px]"></TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Actions</TableHead>
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
                            <TableCell>{getActions(ent.type, downloadFile, ent.path)}</TableCell>
                        </TableRow>
                    ))
                }
                <TableRow>
                    <TableCell>
                        <Avatar>
                            <AvatarImage src='add.svg' />
                            <AvatarFallback>Add</AvatarFallback>
                        </Avatar>
                    </TableCell>
                    <TableCell>
                        <Button onClick={handleButtonClick}>
                            {nameForButton()}
                        </Button>
                        <input
                            type="file"
                            ref={fileInputRef}
                            style={{ display: 'none' }}
                            onChange={handleFileChange}
                        />
                    </TableCell>
                </TableRow>
            </TableBody>
        </Table>
    )
}

export default Filetable
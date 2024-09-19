import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
  } from "@/components/ui/table"

  import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
  } from "@/components/ui/dropdown-menu"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import axios from "axios"
import { useEffect, useRef, useState } from "react"
import { EntityList } from "./content"
import { Button } from "./ui/button"


interface ContentProps {
    entityList: EntityList
    path: string
    type: string
    id: string
    updateTable: (name: string) => void
    downloadFile: (path: string, type: string) => void
    uploadFile: (file: File | undefined, path: string | undefined, id: string) => void
}


function getActions(type: string, downloadFile: (path: string, type: string) => void, path: string) {
    return (
        <>
            <Button onClick={ () => {downloadFile(path, type)} }>Download</Button>
        </>
    )
}


function Filetable( { entityList, path, type, id, updateTable, downloadFile, uploadFile }: ContentProps ){
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleButtonClick = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click();
        } else {
            console.log('fileInputRef.current is null');
        }
    };

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        console.log('id', id)
        const file = event.target.files?.[0];

        uploadFile(file, `${path}/${file?.name}`, id);
        updateTable(path);
    };

    const createEntity = () => {

    };

    const getDropDown = () => {
        if (type === 'folder' || type === 'project') {
            return (
                <>
                    <DropdownMenu>
                        <DropdownMenuTrigger>
                            <Button>
                                Add
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                            <DropdownMenuItem>Folder</DropdownMenuItem>
                            <DropdownMenuItem onClick={handleButtonClick}>
                                File
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                    <input
                        type="file"
                        ref={fileInputRef}
                        style={{ display: 'none' }}
                        onChange={handleFileChange}
                    />
                </>
            )
        }
        else if (type === 'workspace') {
            return (
                <Button onClick={createEntity}>
                    Create Project
                </Button>
            )

        }
        else if (type === '') {
            return (
                <Button onClick={createEntity}>
                    Create Workspace
                </Button>
            )
        }
    }

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
                        {getDropDown()}
                    </TableCell>
                </TableRow>
            </TableBody>
        </Table>
    )
}

export default Filetable
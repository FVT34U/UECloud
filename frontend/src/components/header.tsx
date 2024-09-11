import {
    Menubar,
    MenubarContent,
    MenubarItem,
    MenubarMenu,
    MenubarSeparator,
    MenubarShortcut,
    MenubarTrigger,
  } from "@/components/ui/menubar"
import axios from "axios";
import { useEffect } from "react";

function Header() {
    const getProfile = () => {
        axios.get('http://127.0.0.1:8000/api/users/me', {
            withCredentials: true,
        })
        .then(resp => {
            console.log('api/users/me', resp)
        })
    };

    const checkSignIn = () => {
        
    };

    useEffect(() => {
        checkSignIn()
    }, []);

    return (
        <Menubar className="px-10 py-5 justify-end">
            <MenubarMenu>
                <MenubarTrigger>UECloud</MenubarTrigger>
                    <MenubarContent className="mx-10">
                        <MenubarItem onClick={getProfile}>Profile</MenubarItem>
                        <MenubarItem>Settings</MenubarItem>
                        <MenubarSeparator />
                        <MenubarItem>
                            <a href="/logout">Logout</a>
                        </MenubarItem>
                    </MenubarContent>
            </MenubarMenu>
        </Menubar>
    )
}

export default Header
import {
    Menubar,
    MenubarContent,
    MenubarItem,
    MenubarMenu,
    MenubarSeparator,
    MenubarShortcut,
    MenubarTrigger,
} from "@/components/ui/menubar"

import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
    DialogFooter,
} from "@/components/ui/dialog"
  
import axios from "axios";
import { useEffect, useState, } from "react";
import Cookies from "js-cookie";
import { ProfileForm } from "./login_form";
import { Button } from "./ui/button";


function Header() {
    const getProfile = () => {
        axios.get('https://127.0.0.1:8000/api/users/me', {
            withCredentials: true,
        })
        .then(resp => {
            console.log('api/users/me', resp)
        })
    };

    const checkSignIn = () => {
        console.log('cock', Cookies.get('signIn'));
        return Cookies.get('signIn');
    };

    const doLogout = () => {
        axios.get('https://127.0.0.1:8000/api/logout', {
            withCredentials: true,
        })
        .then(resp => {
            console.log('api/logout', resp)
            if (resp.status === 200) {
                Cookies.set('signIn', 'false')
                setMenuContent(signInMenuItem)
            }
        })
    }

    const signInMenuItem = 
    <MenubarContent className="mx-10">
        <DialogTrigger asChild>
            <MenubarItem>Sign In</MenubarItem>
        </DialogTrigger>
    </MenubarContent>

    const usualMenuItem =
    <MenubarContent className="mx-10">
        <MenubarItem onClick={getProfile}>Profile</MenubarItem>
        <MenubarItem>Settings</MenubarItem>
        <MenubarSeparator />
        <MenubarItem onClick={doLogout}>Logout</MenubarItem>
    </MenubarContent>
    
    const [menuContent, setMenuContent] = useState(signInMenuItem);

    useEffect(() => {
        if (checkSignIn() === undefined) {
            setMenuContent(signInMenuItem)
        }
        else if (checkSignIn() === "false") {
            setMenuContent(signInMenuItem)
        }
        else {
            setMenuContent(usualMenuItem)
        }
    }, []);

    return (
        <Menubar className="px-10 py-5 justify-end">
            <MenubarMenu>
                <MenubarTrigger>UECloud</MenubarTrigger>
                    <Dialog>
                        {menuContent}
                        <DialogContent aria-description="">
                            <DialogHeader>
                                <DialogTitle>Sign In</DialogTitle>
                                <DialogDescription>
                                    You can Sign In here. Enter your credentials and click Submit.
                                </DialogDescription>
                            </DialogHeader>
                            <ProfileForm setMenuContent={setMenuContent} usualMenuItem={usualMenuItem}/>
                        </DialogContent>
                    </Dialog>
            </MenubarMenu>
        </Menubar>
    )
}

export default Header
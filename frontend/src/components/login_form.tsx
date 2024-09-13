"use client"

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import axios from "axios";
import React from "react";
import { DialogClose } from "./ui/dialog";
import Cookies from "js-cookie";

const formSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
  password: z.string().min(2, {
    message: "Password must be at least 2 characters.",
  }),
})

interface MenuContentProps {
	setMenuContent: React.Dispatch<React.SetStateAction<JSX.Element>>;
	usualMenuItem: JSX.Element;
}

export function ProfileForm ( { setMenuContent, usualMenuItem }: MenuContentProps ) {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  })
 
  async function onSubmit(values: z.infer<typeof formSchema>) {
    await axios.postForm(
        "https://127.0.0.1:8000/api/token",
        values,
        { withCredentials: true, }
    )
    .then(resp => {
        console.log('api/token', resp)
		if (resp.status === 200) {
			Cookies.set('signIn', 'true', { expires: 7 });
			setMenuContent(usualMenuItem);
		}
    })

	window.location.reload()
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="jackie-o" {...field} />
              </FormControl>
              <FormDescription>
                This is your public display name.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
            control={form.control}
            name="password"
            render={({ field }) => (
                <FormItem>
                    <FormLabel>Password</FormLabel>
                    <FormControl>
                        <Input type="password" placeholder="2 chars at least)" {...field} />
                    </FormControl>
                    <FormDescription>
                        This is your secret password.
                    </FormDescription>
                    <FormMessage />
                </FormItem>
            )}
        />
		<DialogClose asChild>
        	<Button type="submit">Submit</Button>
		</DialogClose>
      </form>
    </Form>
  )
}

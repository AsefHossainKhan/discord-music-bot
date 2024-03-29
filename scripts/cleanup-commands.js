require('dotenv').config()

const { Client, GatewayIntentBits, REST, Routes } = require('discord.js')

// Construct and prepare an instance of the REST module
const rest = new REST({ version: '10' }).setToken(process.env.TOKEN);

// and deploy your commands!
(async () => {
  try {
    console.log(
      `Started cleaning application (/) commands.`,
    )

    // The put method is used to fully refresh all commands in the guild with the current set
    await rest.put(
      Routes.applicationCommands(process.env.CLIENT_ID),
      { body: [] },
    )

    console.log(
      `Successfully cleaned global application (/) commands.`,
    )
  } catch (error) {
    // And of course, make sure you catch and log any errors!
    console.error(error)
  }
})()

const client = new Client({ intents: [GatewayIntentBits.Guilds] });

// and deploy your commands!
(async () => {
  try {
    await client.login(process.env.TOKEN)

    const guild_ids = client.guilds.cache.map((guild) => guild.id)

    for (let index = 0; index < guild_ids.length; index++) {
      const guildId = guild_ids[index]
      const data = await rest.put(
        Routes.applicationGuildCommands(process.env.CLIENT_ID, guildId),
        { body: [] },
      )
      console.log(
        `Successfully cleaned application (/) guild commands for the guild with guildID = ${guildId}`,
      )
    }

    process.exit(0)
  } catch (error) {
    // And of course, make sure you catch and log any errors!
    console.error(error)
  }
})()

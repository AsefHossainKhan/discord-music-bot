const { SlashCommandBuilder } = require('discord.js')

module.exports = {
  data: new SlashCommandBuilder().setName('joindate').
    setDescription('Provides information about the join date of the user.').
    addUserOption((option) => option.setName('target').
      setDescription('The user').
      setRequired(true)), async execute (interaction) {
    const member = interaction.options.getUser('target')
    const guildMember = await interaction.guild.members.fetch(member)
    await interaction.reply(
      `${member.username} joined on ${guildMember.joinedAt}.`)
  },
}
